import json
import sys
import logging
logging.basicConfig(level=logging.DEBUG)

from Services.WriterService import WriterService


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

    def read_from_local(self, block_hash):
        block_file_path = self.writer_service.config['LOCAL_PATH'] + block_hash + ".json"
        with open(block_file_path, "r") as read_file:
            data = json.load(read_file)
        return data


    def read_from_hdfs(self, block_hash):
        try:
            from hdfs3 import HDFileSystem
            hdfs = HDFileSystem(host = self.writer_service.config['HDFS_HOST'], port = self.writer_service.config['HDFS_PORT'])
            block_file_path = self.writer_service.config['HDFS_PATH'] + block_hash + ".json"
            with hdfs.open(block_file_path) as read_file:
                data = json.load(read_file)
            return data
        except ImportError:
            logging.error("hdfs3 module not found")
        except:
            logging.error("Error in connecting to hadoop")


    def read_transaction(self, block_file_path, transaction_hash):
        
        mode = self.writer_service.config['MODE']

        if mode == "local":
            data = self.read_from_local(block_file_path)
        elif mode == "hadoop":
            data = self.read_from_hdfs(block_file_path)
       
        transaction = data['transactions'][transaction_hash]
        logging.info("Transaction read from the blockchain:")
        logging.info(transaction)

        return transaction

    def read_block(self, block_hash):
        mode = self.writer_service.config['MODE']

        if mode == "local":
            block = self.read_from_local(block_hash)
        elif mode == "hadoop":
            block = self.read_from_hdfs(block_hash)

        return block

    def read_block_chain(self):
        logging.info("Blockchain is being read\n")
        head_block_hash = self.writer_service.get_head_block_hash()
        current_block_hash = head_block_hash

        block_list = []

        while current_block_hash != WriterService.DEFAULT_PREV_HASH:
            current_block = self.read_block(current_block_hash)
            block_list.insert(0, current_block)

            current_block_hash = current_block["prev_block_hash"]

        return block_list
