import json
from Models import Block, Transaction


class TransactionsPoolingService:
    '''
        Used to maintain a map of mined transaction's ID and the corresponding
        block number. Used to check for duplicate transactions and also acts
        as an index, to retrieve a transaction from the blockchain.
    '''
    __instance = None

    def __init__(self):
        if TransactionsPoolingService.__instance is not None:
            raise Exception("Singleton instance already exists. Use TransactionsPoolingService.get_instance() to get that instance.")
        
        self.mined_transactions = {}
        TransactionsPoolingService.__instance = self

    @staticmethod
    def get_instance():
        if TransactionsPoolingService.__instance is None:
            return TransactionsPoolingService()
        return TransactionsPoolingService.__instance

    def transaction_exists(self, transaction_id):
        if transaction_id in self.mined_transactions:
            return True
        return False

    def add_transaction(self, transaction_id, block_number):
        self.mined_transactions[transaction_id] = block_number

    def get_block_number(self, transaction_id):
        return self.mined_transactions[transaction_id]
