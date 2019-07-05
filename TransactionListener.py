#!/usr/bin/python3
import json

import falcon
from wsgiref import simple_server

from falcon_cors import CORS

from Models import Transaction
from Services.MiningService import MiningService
from Services.ReaderService import ReaderService
from Services.WriterService import WriterService
from Services.TransactionsPoolingService import TransactionsPoolingService

mining_service = MiningService.get_instance()
writer_service = WriterService.get_instance()
reader_service = ReaderService.get_instance()
transaction_pooling_service = TransactionsPoolingService.get_instance()

unmined_transactions = []


# function to check if the transaction already exists in the unmined pool or
# other validations regarding the conventions defined for a transaction
def validate_transaction(transaction):
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


# Read the complete Blockchain, if it exists
block_chain = reader_service.read_block_chain()

# Add each transaction ID to the transaction pooling service
for block in block_chain:
    block_number = block['block_number']
    for transaction in block['transactions']:
        transaction_pooling_service.add_transaction(transaction, block_number)

# Instantiate Falcon API application
cors_allow_all = CORS(allow_all_origins=True,
                      allow_all_headers=True,
                      allow_all_methods=True)

api = falcon.API(middleware=[cors_allow_all.middleware])
api.req_options.auto_parse_form_urlencoded = True
api.add_route('/transaction', TransactionsHandler())
api.add_route('/block/all', BlockChainHandler())

httpd = simple_server.make_server('127.0.0.1', 8000, api)
print("Listening for transactions ...")
httpd.serve_forever()
