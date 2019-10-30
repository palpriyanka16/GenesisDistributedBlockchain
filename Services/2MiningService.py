from hashlib import md5
import logging
logging.basicConfig(format='[ %(asctime)s ] %(levelname)s: <%(name)s>: %(message)s')

from Models import Block
from Services.WriterService import WriterService


class MiningService:
    TRANSACTIONS_PER_BLOCK = 2

    logger = logging.getLogger(name="MiningService")
    __instance = None
    __mining_difficulty = 20     # num of initial bits to be zero in the block hash
    __max_nonce = 2**32         # nonce is usually a 32 bit integer
    writer_service = WriterService.get_instance()

    @staticmethod
    def get_instance():
        if MiningService.__instance is None:
            return MiningService()
        return MiningService.__instance

    def __init__(self):
        # This condition is to make sure that the constructor isn't directly called
        # more than once by any clients
        if MiningService.__instance is not None:
            raise Exception("Singleton instance already exists. Use MiningService.get_instance() to get that instance.")
        MiningService.__instance = self

    # function to check if the hash satisfies the difficulty condition in mining
    def satisfies_difficulty(self, hashed_value_in_hex):
        # number of bits in the given hash
        total_number_of_bits = len(hashed_value_in_hex) * 4

        hashed_value_in_int = int(hashed_value_in_hex, 16)
        # if the hashed value is less that 1 followed by (total_number_of_bits - self.__mining_difficulty) zeros
        # in the binary form, it means the hashed value has a minimum of self.__mining_difficulty zeros in the
        # beginning
        return hashed_value_in_int < 2**(total_number_of_bits - self.__mining_difficulty)

    def mine(self, transaction_list):
        if len(transaction_list) > MiningService.TRANSACTIONS_PER_BLOCK:
            raise Exception("Transactions count should be less than " + str(MiningService.TRANSACTIONS_PER_BLOCK) + 1)

        block_number = self.writer_service.get_head_block_number() + 1
        self.logger.info("Starting to mine Block {} ...".format(block_number))
        prev_block_hash = self.writer_service.get_head_block_hash()
        block_data_without_nonce = Block.block_data_without_nonce(block_number, prev_block_hash, transaction_list)

        transactions = {}
        for t in transaction_list:
            transactions[t.get_id()] = t
            self.logger.info("Adding transaction {} to block".format(t.get_id()))

        nonce = 0
        logging.info("Mining block : " + str(block_number))
        while nonce < self.__max_nonce:
            block_data = block_data_without_nonce + str(nonce)
            block_data_hash = md5(block_data.encode()).hexdigest()
            if self.satisfies_difficulty(block_data_hash):
                logging.info("Block " + str(block_number) + " mined with nonce " + str(nonce) + " : ")
                self.logger.info("Block {} mined with nonce {}".format(block_number, nonce))
                #print(bin(int(block_data_hash, 16))[2:].zfill(len(block_data_hash) * 4))
                block = Block(block_number, prev_block_hash, transactions, nonce, block_data_hash)
                self.logger.debug(block.convert_to_dict())
                self.writer_service.write(block_data_hash, block)
                break
            nonce += 1

        # Ideally, we should shuffle the transactions and repeat the process till we get a valid nonce
        if nonce == self.__max_nonce:
            raise Exception("Couldn't find a valid nonce for the data.")
