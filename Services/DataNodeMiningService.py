from hashlib import md5
import logging
logging.basicConfig(level=logging.DEBUG)

from Models import Block
from Services.WriterService import WriterService
from Services.NetworkService import NetworkService


class DataNodeMiningService:
    TRANSACTIONS_PER_BLOCK = 2
    MASTER_ADDRESS = ""

    __instance = None
    __mining_difficulty = 20     # num of initial bits to be zero in the block hash
    __max_nonce = 2**32         # nonce is usually a 32 bit integer
    writer_service = WriterService.get_instance()
    network_service = NetworkService.get_instance()

    @staticmethod
    def get_instance():
        if DataNodeMiningService.__instance is None:
            return DataNodeMiningService()
        return DataNodeMiningService.__instance

    def __init__(self):
        # This condition is to make sure that the constructor isn't directly called
        # more than once by any clients
        if DataNodeMiningService.__instance is not None:
            raise Exception("Singleton instance already exists. Use DataNodeMiningService.get_instance() to get that instance.")
        DataNodeMiningService.__instance = self

    # function to check if the hash satisfies the difficulty condition in mining
    def satisfies_difficulty(self, hashed_value_in_hex):
        # number of bits in the given hash
        total_number_of_bits = len(hashed_value_in_hex) * 4

        hashed_value_in_int = int(hashed_value_in_hex, 16)
        # if the hashed value is less that 1 followed by (total_number_of_bits - self.__mining_difficulty) zeros
        # in the binary form, it means the hashed value has a minimum of self.__mining_difficulty zeros in the
        # beginning
        return hashed_value_in_int < 2**(total_number_of_bits - self.__mining_difficulty)

    def mine(self, block_data_without_nonce, nonce_start, nonce_end):
        logging.info("Mining block with nonce range " + str(nonce_start) + ", " + str(nonce_end))
        valid_nonce = -1
        block_hash_without_nonce = md5(block_data_without_nonce.encode()).hexdigest()

        for nonce in range(nonce_start, nonce_end):
            block_data = block_data_without_nonce + str(nonce)
            block_data_hash = md5(block_data.encode()).hexdigest()

            if self.satisfies_difficulty(block_data_hash):
                logging.info("Block mined with nonce " + str(nonce) + " : ")
                valid_nonce = nonce

                self.network_service.send_valid_nonce_to_master(
                    valid_nonce,
                    block_hash_without_nonce,
                    self.MASTER_ADDRESS
                )

                # print(bin(int(block_data_hash, 16))[2:].zfill(len(block_data_hash) * 4))
                break
            nonce += 1

        # Ideally, we should shuffle the transactions and repeat the process till we get a valid nonce
        if valid_nonce == -1:
            self.network_service.inform_master_nonce_not_in_range(block_hash_without_nonce, self.MASTER_ADDRESS)
            raise Exception("Couldn't find a valid nonce for the data.")
