import json
import logging

from Models import Block, Transaction

logger = logging.getLogger('TransactionPoolingService')


class TransactionsPoolingService:
    '''
        mined_transactions:
        Used to maintain a map of mined transaction's ID and the corresponding
        block number. Used to check for duplicate transactions and also acts
        as an index, to retrieve a transaction from the blockchain.

        unmined_transactions:
        Used to maintain a list of unmined transactions. Used to check for
        duplicate transactions.
    '''
    __instance = None

    def __init__(self):
        if TransactionsPoolingService.__instance is not None:
            raise Exception("Singleton instance already exists. Use TransactionsPoolingService.get_instance() to get that instance.")
        
        self.mined_transactions = {}
        self.unmined_transactions = []
        TransactionsPoolingService.__instance = self

    @staticmethod
    def get_instance():
        if TransactionsPoolingService.__instance is None:
            return TransactionsPoolingService()
        return TransactionsPoolingService.__instance

    def get_transaction_id(self, transaction):
        '''
            Returns the transaction ID, if a 'Transaction' object is passed
            as an argument, else, if it is a transaction ID (str),
            return the same value.
        '''
        if isinstance(transaction, Transaction):
            return transaction.get_id()
        return transaction        

    def is_mined_transaction(self, transaction):
        transaction_id = self.get_transaction_id(transaction)
        if transaction_id in self.mined_transactions:
            return True
        return False

    def add_mined_transaction(self, transaction, block_number):
        transaction_id = self.get_transaction_id(transaction)
        self.mined_transactions[transaction_id] = block_number

    def get_block_number(self, transaction):
        transaction_id = self.get_transaction_id(transaction)
        return self.mined_transactions[transaction_id]

    def add_unmined_transaction(self, transaction):
        if not isinstance(transaction, Transaction):
            raise TypeError("Expected argument type 'Transaction'")
        self.unmined_transactions.append(transaction)

    def is_unmined_transaction(self, transaction):
        if not isinstance(transaction, Transaction):
            raise TypeError("Expected argument type 'Transaction'")

        # Check if a transaction exists in the unmined_transactions list
        # Inefficient approach, but works, for now 
        for t in self.unmined_transactions:
            if t.get_id() == transaction.get_id():
                return True
        return False

    def delete_unmined_transaction_if_exists(self, transaction):
        if not isinstance(transaction, Transaction):
            raise TypeError("Expected argument type 'Transaction'")
        
        transaction_id = transaction.get_id()

        for (i, v) in enumerate(self.unmined_transactions):
            if v.get_id() == transaction_id:
                del self.unmined_transactions[i]
                return

    def is_new_transaction(self, transaction):
        if not self.is_mined_transaction(transaction) and not self.is_unmined_transaction(transaction):
            return True
        return False

    # Function to clean up transactions pool when the blockchain is reset
    def clean_transactions_pool(self):
        self.mined_transactions.clear()
        # No need to clear unmined transactions as the write method in writer service
        # itself cleans unmined_transactions when inserting into the blockchain. So,
        # only the transactions not added in the blockchain will be left in unmined_transactions.
