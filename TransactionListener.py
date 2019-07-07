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

forwarding_service = ForwardingService.get_instance()
mining_service = MiningService.get_instance()
reader_service = ReaderService.get_instance()
writer_service = WriterService.get_instance()

unmined_transactions = []


# function to check if the transaction already exists in the unmined pool or
# other validations regarding the conventions defined for a transaction
def validate_transaction(transaction):
    pass


# function to verify and signatures and hashes for transactions and block data
def validate_block(block):
    pass


def mine_transactions():
    if len(unmined_transactions) >= MiningService.TRANSACTIONS_PER_BLOCK:
        mining_service.mine(unmined_transactions[:MiningService.TRANSACTIONS_PER_BLOCK])
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

        validate_transaction(t)

        unmined_transactions.append(t)  # Add the transaction to the unmined transaction pool

        mine_transactions()

        response = {'status': 'success'}
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
print("Listening in http://localhost:8000...")
httpd.serve_forever()
