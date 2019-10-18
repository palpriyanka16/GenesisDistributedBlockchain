#!/usr/bin/python3
import hashlib
import json
import logging
logging.basicConfig(level=logging.DEBUG)

import falcon
from wsgiref import simple_server

from falcon_cors import CORS

from Models import Block, Transaction
from Services.DataNodeMiningService import DataNodeMiningService
from Services.NetworkService import NetworkService
from Services.PoolMiningService import PoolMiningService
from Services.ReaderService import ReaderService
from Services.WriterService import WriterService
from Services.TransactionsPoolingService import TransactionsPoolingService

data_node_mining_service = DataNodeMiningService.get_instance()
network_service = NetworkService.get_instance()
pool_mining_service = PoolMiningService.get_instance()
reader_service = ReaderService.get_instance()
writer_service = WriterService.get_instance()
transaction_pooling_service = TransactionsPoolingService.get_instance()


def validate_transaction(transaction):
    '''
        Function to check if the transaction already exists with this node, 
        either mined or unmined; also checks if the transaction has a
        valid signature.
        Returns true or false accordingly.
    '''

    logging.info("Transaction is being validated")
    # Check if it is a new transaction
    if not transaction_pooling_service.is_new_transaction(transaction):
        logging.error("Duplicate transaction: {}".format(transaction.get_id()))
        return False

    # Check if the signature is valid
    if not transaction.verify():
        logging.error("Invalid transaction: {}".format(transaction.get_id()))
        return False
    logging.info("Transaction validated successfully.\n")
    return True

# function to verify and signatures and hashes for transactions and block data
def validate_block(block):
    logging.info("Validating block...")
    transactions_list = []
    for transaction in block.transactions.values():
        transactions_list.append(transaction)
    block_data_without_nonce = Block.block_data_without_nonce(block.block_number, block.prev_block_hash, transactions_list)
    block_data = block_data_without_nonce + str(block.nonce)
    block_data_hash = hashlib.md5(block_data.encode()).hexdigest()
    
    if not pool_mining_service.satisfies_difficulty(block_data_hash):
        logging.error("Nonce of the block does not meet mining criteria")
        return False

    for transaction in block.transactions.values():
        if not transaction.verify():
            logging.error("Transaction with an invalid signature encountered")
            return False
    logging.info("Block validated successfully.\n")
    return True


# function to validate only the new blocks to check if it can be appended to
# the existing blockchain
def validate_new_block_header(block):
    if writer_service.get_head_block_number() + 1 != block.block_number:
        return False
    if writer_service.get_head_block_hash() != block.prev_block_hash:
        return False
    return True


def mine_transactions():
    unmined_transactions = transaction_pooling_service.unmined_transactions

    if len(unmined_transactions) >= PoolMiningService.TRANSACTIONS_PER_BLOCK:
        transactions_to_mine = unmined_transactions[:PoolMiningService.TRANSACTIONS_PER_BLOCK]
        # mining_service.mine(transactions_to_mine)
        pool_mining_service.mine_new_transaction_set(transactions_to_mine)


class TransactionsHandler:

    def on_get(self, req, resp):
        blockHash = req.get_param("blockHash")
        txHash = req.get_param("txHash")
        logging.info("Searching for transaction "+ txHash + " in  block " + blockHash)
        transaction = reader_service.read_transaction(blockHash, txHash)

        response = {'status': 'success', 'data': transaction} ## response will contain the transaction json also
        response = json.dumps(response)
        resp.body = response

    def on_post(self, req, resp):
        # TODO: Change the input data format to be 'json', see BlocksHandler
        sender = req.params['sender']
        transaction_data = req.params['data']
        signature = req.params['signature']
        t = Transaction(sender, transaction_data, signature)
        if validate_transaction(t):
            # Add the transaction to the unmined transactions list
            transaction_pooling_service.unmined_transactions.append(t)
            logging.info("Received Transaction has been added to unmined transactions.\n")
            logging.info(len(transaction_pooling_service.unmined_transactions))
            # network_service.broadcast_transaction(t)
            mine_transactions()
            response = {'status': 'Success'}

        else:
            response = {'status': 'Failed'}

        response = json.dumps(response)
        resp.body = response


class BlockChainHandler:

    def on_get(self, req, resp):
        block_chain = reader_service.read_block_chain()

        response = {'status': 'success', 'data': block_chain}
        response = json.dumps(response)
        resp.body = response


def validate_and_insert_block(block, sender):
    if validate_new_block_header(block):
        if validate_block(block):
            writer_service.write(block.block_hash, block)
        else:
            logging.error("Received block is invalid")
    elif block.block_number > writer_service.get_head_block_number():
        new_blockchain = network_service.fetch_blockchain_from(sender)

        writer_service.remove_existing_blockchain()
        for block in new_blockchain:
            validate_and_insert_block(block, sender)
    else:
        print("Dropping received block...")


class BlocksHandler:

    def on_post(self, req, resp):
        data = json.loads(req.stream.read().decode())

        new_block_json = data['block']
        new_block = Block.load_from_json(new_block_json)

        sender = data['sender']

        logging.info("Received new block")

        validate_and_insert_block(new_block, sender)
        response = {'status': 'success'}
        response = json.dumps(response)
        resp.body = response


class BlockMiningHandler:

    def on_post(self, req, resp):
        data = json.loads(req.stream.read().decode())

        block_data_without_nonce = data['block']
        data_node_mining_service.mine(block_data_without_nonce, data["nonce_start"], data["nonce_end"])


# Read the complete Blockchain, if it exists
block_chain = reader_service.read_block_chain()

# Add each transaction ID to the transaction pooling service
for block in block_chain:
    block_number = block['block_number']
    for transaction in block['transactions']:
        transaction_pooling_service.add_mined_transaction(transaction, block_number)

# Instantiate Falcon API application
cors_allow_all = CORS(allow_all_origins=True,
                      allow_all_headers=True,
                      allow_all_methods=True)

api = falcon.API(middleware=[cors_allow_all.middleware])
api.req_options.auto_parse_form_urlencoded = True
api.add_route('/transaction', TransactionsHandler())
api.add_route('/block/all', BlockChainHandler())
api.add_route('/block', BlocksHandler())
api.add_route('/block/mine', BlockMiningHandler())

# httpd = simple_server.make_server('127.0.0.1', 8000, api)
# print("Listening for newer transactions on http://localhost:8000/transaction")
# httpd.serve_forever()
