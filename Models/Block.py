
from .Transaction import Transaction

class Block:

    def __init__(self, block_number, prev_block_hash, transactions, nonce, block_hash):
        self.block_number = block_number
        self.prev_block_hash = prev_block_hash
        self.nonce = nonce
        self.transactions = transactions
        self.block_hash = block_hash

    def __str__(self):
        header = "Block Number: {}\nPrevious Block Hash: {}\n".format(self.block_number, self.prev_block_hash)
        transactions = '\n'.join([x for x in self.transactions])
        return header + transactions

    @staticmethod
    def block_data_without_nonce(block_number, prev_block_hash, transaction_list):
        t = str(block_number) + prev_block_hash + ''.join(str(e) for e in transaction_list)
        return t

    @staticmethod
    def load_from_json(block_json):
        # Creates a 'Block' from the block's JSON data
        prev_block_hash = block_json['prev_block_hash']
        block_hash = block_json['block_hash']
        block_number = block_json['block_number']
        nonce = block_json['nonce']

        transactions_dict = {}
        for t in block_json['transactions']:
            transaction_data = block_json['transactions'][t]
            transaction = Transaction(transaction_data['sender'], 
                                      transaction_data['data'], 
                                      transaction_data['signature'])
            transactions_dict[t] = transaction

        block = Block(block_number, prev_block_hash, transactions_dict, nonce, block_hash)
        return block

    def convert_to_dict(self):
        t = {
            'block_number': self.block_number,
            'prev_block_hash': self.prev_block_hash,
            'nonce': self.nonce
        }
        transactions_dict = {}
        for key in self.transactions.keys():
            transactions_dict[key] = self.transactions[key].__dict__
        t['transactions'] = transactions_dict
        t['block_hash'] = self.block_hash

        return t

