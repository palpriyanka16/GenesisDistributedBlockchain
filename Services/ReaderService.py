import json
import sys
from Services.WriterService import WriterService
from hdfs3 import HDFileSystem

mode = sys.argv[1]

class ReaderService:
    __instance = None
    writer_service = WriterService.get_instance()

    def __init__(self):
        if ReaderService.__instance is not None:
            raise Exception("Singleton instance already exists. Use ReaderService.get_instance() to get that instance.")
        ReaderService.__instance = self

    @staticmethod
    def get_instance():
        if ReaderService.__instance is None:
            return ReaderService()
        return ReaderService.__instance

    def read_transaction(self, block_file_path, transaction_hash):
        # might be replaced by a hdfs command to read file
        if mode == "local":
            block_file_path = './BlockChain/' + block_file_path + ".json"
            with open(block_file_path, "r") as read_file:
                data = json.load(read_file)
        elif mode == "hadoop":
            hdfs = HDFileSystem(host='localhost', port=9000)
            block_file_path = '/user/BlockChain/' + block_file_path + ".json"
            with hdfs.open(block_file_path) as read_file:
                data = json.load(read_file)
       

        transaction = data['transactions'][transaction_hash]
        print("Transaction read from the blockchain:")
        print(transaction)

        return transaction

    def read_block(self, block_hash):
        
        if mode == "local":
            block_file_path = './BlockChain/' + block_hash + ".json"
            with open(block_file_path, "r") as read_file:
                block = json.load(read_file)
        elif mode == "hadoop":
            hdfs = HDFileSystem(host='localhost', port=9000)
            block_file_path = '/user/BlockChain/' + block_hash + ".json"
            with hdfs.open(block_file_path) as read_file:
               block = json.load(read_file)


        return block

    def read_block_chain(self):
        head_block_hash = self.writer_service.get_head_block_hash()
        current_block_hash = head_block_hash

        block_list = []

        while current_block_hash != WriterService.DEFAULT_PREV_HASH:
            current_block = self.read_block(current_block_hash)
            block_list.insert(0, current_block)

            current_block_hash = current_block["prev_block_hash"]

        return block_list
