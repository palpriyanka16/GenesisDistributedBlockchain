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
    cur_block_in_buffer = ""
    cur_block_hash_in_buffer = ""


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

    def mine_new_transaction_set(self, transaction_list):
        if len(transaction_list) > PoolMiningService.TRANSACTIONS_PER_BLOCK:
            raise Exception("Transactions count should be less than " + str(PoolMiningService.TRANSACTIONS_PER_BLOCK) + 1)

        block_number = self.writer_service.get_head_block_number() + 1
        prev_block_hash = self.writer_service.get_head_block_hash()
        block_data_without_nonce = Block.block_data_without_nonce(block_number, prev_block_hash, transaction_list)
        self.cur_block_in_buffer = block_data_without_nonce
        self.cur_block_hash_in_buffer = md5(block_data_without_nonce.encode()).hexdigest()

        block_with_nonce_range = {}
        block_with_nonce_range["block"] = block_data_without_nonce

        for data_node in self.DATA_NODES_ADDRESS:
            block_with_nonce_range["nonce_start"] = self.cur_nonce_start_value
            block_with_nonce_range["nonce_end"] = self.cur_nonce_start_value + self.NONCE_RANGE_PER_NODE

            self.network_service.send_block_for_mining(data_node, block_with_nonce_range)
            self.cur_nonce_start_value += self.NONCE_RANGE_PER_NODE

    def reset_pool(self):
        self.cur_nonce_start_value = 0
        self.cur_block_in_buffer = ""
        self.cur_block_hash_in_buffer = ""

    def send_next_nonce_range(self, to):
        block_with_nonce_range = {}
        block_with_nonce_range["block"] = self.cur_block_in_buffer
        block_with_nonce_range["block_hash"] = self.cur_block_hash_in_buffer
        block_with_nonce_range["nonce_start"] = self.cur_nonce_start_value
        block_with_nonce_range["nonce_end"] = self.cur_nonce_start_value + self.NONCE_RANGE_PER_NODE

        self.network_service.send_block_for_mining(to, block_with_nonce_range)
        self.cur_nonce_start_value += self.NONCE_RANGE_PER_NODE
