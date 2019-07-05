#!/usr/bin/python3
import json

import falcon
from wsgiref import simple_server

from falcon_cors import CORS

from Models import Block, Transaction
from Services.ForwardingService import ForwardingService
from Services.MiningService import MiningService
from Services.ReaderService import ReaderService
from Services.WriterService import WriterService
from Services.TransactionsPoolingService import TransactionsPoolingService

forwarding_service = ForwardingService.get_instance()
mining_service = MiningService.get_instance()
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

    # Check if it is a new transaction
    if not transaction_pooling_service.is_new_transaction(transaction):
        print("Duplicate transaction: {}".format(transaction.get_id()))
        return False

    # Check if the signature is valid
    if not transaction.verify():
        print("Invalid transaction: {}".format(transaction.get_id()))
        return False
    return True

# function to verify and signatures and hashes for transactions and block data
def validate_block(block):
    pass


def mine_transactions():
    unmined_transactions = transaction_pooling_service.unmined_transactions

    if len(unmined_transactions) >= MiningService.TRANSACTIONS_PER_BLOCK:
        transactions_to_mine = unmined_transactions[:MiningService.TRANSACTIONS_PER_BLOCK]
        mining_service.mine(transactions_to_mine)
        del unmined_transactions[:MiningService.TRANSACTIONS_PER_BLOCK]


class TransactionsHandler:

    def on_get(self, req, resp):
        blockHash = req.get_param("blockHash")
        txHash = req.get_param("txHash")

        transaction = reader_service.read_transaction(blockHash, txHash)

        response = {'status': 'success', 'data': transaction} ## response will contain the transaction json also
        response = json.dumps(response)
        resp.body = response

    def on_post(self, req, resp):
        sender = req.params['sender']
        transaction_data = req.params['data']
        signature = req.params['signature']
        t = Transaction(sender, transaction_data, signature)

        if validate_transaction(t):
            # Add the transaction to the unmined transactions list
            transaction_pooling_service.unmined_transactions.append(t)
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


class BlocksHandler:

    def on_post(self, req, resp):
        new_block_json = json.loads(req.params['block_data'])
        new_block = Block.load_from_json(new_block_json)

        validate_block(new_block)

        if writer_service.get_head_block_number() + 1 != new_block.block_number:
            response = {'status': 'failure', 'message': 'Invalid block number.'}
            response = json.dumps(response)
            resp.body = response
        else:
            writer_service.write(new_block.block_hash, new_block)

            response = {'status': 'success'}
            response = json.dumps(response)
            resp.body = response


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

httpd = simple_server.make_server('127.0.0.1', 8000, api)
print("Listening for newer transactions on http://localhost:8000/transaction")
httpd.serve_forever()
