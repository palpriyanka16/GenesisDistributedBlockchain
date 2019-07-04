#!/usr/bin/python3

import json
import sys
import subprocess
from Models import Block, Transaction
from hdfs3 import HDFileSystem


class WriterService:
    __instance = None
    head_block = None
    DEFAULT_PREV_HASH = ""
    config = None

    def __init__(self):
        if WriterService.__instance is not None:
            raise Exception("Singleton instance already exists. Use WriterService.get_instance() to get that instance.")
        WriterService.__instance = self
        with open('./config.json', 'r') as f:
            self.config = json.load(f)


        # The 'head_block_hash' file, if exists, stores the block hash of the head block.
        # Check to see if the file exists, and if so, read the corresponding 
        # block, and assign it to the head_block property
        try:
            with open("./BlockChain/head_block_hash") as f:
                head_block_hash = f.read()

            with open("./BlockChain/" + head_block_hash + ".json") as f:
                block_json = json.loads(f.read())
                self.head_block = Block.load_from_json(head_block_hash, block_json)

        except FileNotFoundError:
            pass

    @staticmethod
    def get_instance():
        if WriterService.__instance is None:
            return WriterService()
        return WriterService.__instance

    def get_head_block_number(self):
        if self.head_block is None:
            return -1
        return self.head_block.block_number

    def get_head_block_hash(self):
        if self.head_block is None:
            return self.DEFAULT_PREV_HASH
        return self.head_block.block_hash

    def write_to_local(self, block_json, file_for_block):
        with open(self.config['LOCAL_PATH'] + file_for_block, 'w') as f:  # writing JSON object
            f.write(block_json)

    def write_to_hdfs(self, file_for_block):
        hdfs = HDFileSystem(host = self.config['HDFS_HOST'], port = self.config['HDFS_PORT'])
        hdfs.touch(self.config['HDFS_PATH'] + file_for_block)
        hdfs.put(self.config['LOCAL_PATH'] + file_for_block, self.config['HDFS_PATH'] + file_for_block)


    def write(self, block_hash, block):
        file_for_block = block_hash + '.json'
        

        block_json = json.dumps(block.convert_to_dict())

        self.write_to_local(block_json, file_for_block)

        mode = self.config['MODE']
        print("Mode: " + mode)

        if mode == "hadoop":
            self.write_to_hdfs(file_for_block)

        self.head_block = block
        self.update_head_block_hash(block_hash)

    def update_head_block_hash(self, block_hash):
        with open("./BlockChain/head_block_hash", "w") as f:
            f.write(block_hash)
