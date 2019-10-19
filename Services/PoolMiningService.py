from hashlib import md5
import logging
logging.basicConfig(level=logging.DEBUG)

from Models import Block
from Services.NetworkService import NetworkService
from Services.WriterService import WriterService


class PoolMiningService:
    TRANSACTIONS_PER_BLOCK = 2
    NONCE_RANGE_PER_NODE = 200000
    DATA_NODES_ADDRESS = ["localhost:8000"]

    __instance = None
    __mining_difficulty = 20     # num of initial bits to be zero in the block hash
    __max_nonce = 2**32         # nonce is usually a 32 bit integer
    writer_service = WriterService.get_instance()
    network_service = NetworkService.get_instance()
    cur_nonce_start_value = 0
    cur_block_in_buffer = {
        "block_data_without_nonce": "",
        "block_hash": "",
        "block_number": 0,
        "prev_block_hash": "",
        "transactions": {}
    }

    @staticmethod
    def get_instance():
        if PoolMiningService.__instance is None:
            return PoolMiningService()
        return PoolMiningService.__instance

    def __init__(self):
        # This condition is to make sure that the constructor isn't directly called
        # more than once by any clients
        if PoolMiningService.__instance is not None:
            raise Exception("Singleton instance already exists. Use PoolMiningService.get_instance() to get that instance.")
        PoolMiningService.__instance = self

    # function to check if the hash satisfies the difficulty condition in mining
    def satisfies_difficulty(self, hashed_value_in_hex):
        # number of bits in the given hash
        total_number_of_bits = len(hashed_value_in_hex) * 4

        hashed_value_in_int = int(hashed_value_in_hex, 16)
        # if the hashed value is less that 1 followed by (total_number_of_bits - self.__mining_difficulty) zeros
        # in the binary form, it means the hashed value has a minimum of self.__mining_difficulty zeros in the
        # beginning
        return hashed_value_in_int < 2**(total_number_of_bits - self.__mining_difficulty)

    def mine_new_transaction_set(self, transaction_list):
        if len(transaction_list) > PoolMiningService.TRANSACTIONS_PER_BLOCK:
            raise Exception("Transactions count should be less than " + str(PoolMiningService.TRANSACTIONS_PER_BLOCK) + 1)

        transactions = {}
        for t in transaction_list:
            transactions[t.get_id()] = t
        block_number = self.writer_service.get_head_block_number() + 1
        prev_block_hash = self.writer_service.get_head_block_hash()
        block_data_without_nonce = Block.block_data_without_nonce(block_number, prev_block_hash, transaction_list)

        self.cur_block_in_buffer = {
            "block_data_without_nonce": block_data_without_nonce,
            "block_hash": md5(block_data_without_nonce.encode()).hexdigest(),
            "block_number": block_number,
            "prev_block_hash": prev_block_hash,
            "transactions": transactions
        }

        block_with_nonce_range = {
            "block": block_data_without_nonce
        }

        for data_node in self.DATA_NODES_ADDRESS:
            block_with_nonce_range["nonce_start"] = self.cur_nonce_start_value
            block_with_nonce_range["nonce_end"] = self.cur_nonce_start_value + self.NONCE_RANGE_PER_NODE

            self.network_service.send_block_for_mining(data_node, block_with_nonce_range)
            self.cur_nonce_start_value += self.NONCE_RANGE_PER_NODE

    def reset_pool(self):
        self.cur_nonce_start_value = 0
        self.cur_block_in_buffer = {
            "block_data_without_nonce": "",
            "block_hash": "",
            "block_number": 0,
            "prev_block_hash": "",
            "transactions": {}
        }

    def send_next_nonce_range(self, to, block_hash):
        logging.info("\n\n\n")
        if block_hash != self.cur_block_in_buffer["block_hash"]:
            logging.info(block_hash)
            logging.info(self.cur_block_in_buffer["block_hash"])
            logging.error("block_hash not equal to hash in buffer...\n\n\n\n")
            return

        block_with_nonce_range = {
            "block": self.cur_block_in_buffer["block_data_without_nonce"],
            "nonce_start": self.cur_nonce_start_value,
            "nonce_end": self.cur_nonce_start_value + self.NONCE_RANGE_PER_NODE
        }

        self.network_service.send_block_for_mining(to, block_with_nonce_range)
        self.cur_nonce_start_value += self.NONCE_RANGE_PER_NODE

    def validate_and_add_block(self, nonce, block_hash):
        logging.info("\n\n\n")
        if block_hash != self.cur_block_in_buffer["block_hash"]:
            logging.info(block_hash)
            logging.info(self.cur_block_in_buffer["block_hash"])
            logging.error("block_hash not equal to hash in buffer...\n\n\n\n")
            return

        block_data = self.cur_block_in_buffer["block_data_without_nonce"] + str(nonce)
        block_data_hash = md5(block_data.encode()).hexdigest()
        if not self.satisfies_difficulty(block_data_hash):
            logging.error("Nonce of the block does not meet mining criteria")
            return


        block = Block(
            self.cur_block_in_buffer["block_number"],
            self.cur_block_in_buffer["prev_block_hash"],
            self.cur_block_in_buffer["transactions"],
            nonce,
            block_data_hash
        )
        self.reset_pool()
        logging.info(block.convert_to_dict())
        self.writer_service.write(block_data_hash, block)
