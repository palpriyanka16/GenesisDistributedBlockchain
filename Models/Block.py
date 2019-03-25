class Block:

    def __init__(self, block_number, prev_block_hash, transactions, nonce, block_hash):
        self.block_number = block_number
        self.prev_block_hash = prev_block_hash
        self.nonce = nonce
        self.transactions = transactions
        self.block_hash = block_hash

    # def add_transaction(self, transaction):
    #     trans_id = transaction.get_id()
    #     self.transactions[trans_id] = transaction

    def __str__(self):
        header = "Block Number: {}\nPrevious Block Hash: {}\n".format(self.block_number, self.prev_block_hash)
        transactions = '\n'.join([x for x in self.transactions])
        return header + transactions

    @staticmethod
    def block_data_without_nonce(block_number, prev_block_hash, transaction_list):
        t = str(block_number) + prev_block_hash + ''.join(str(e) for e in transaction_list)
        return t

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
