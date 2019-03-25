#!/usr/bin/python3

import json
import subprocess
from Models import Block, Transaction


class WriterService:
    __instance = None
    head_block = None
    DEFAULT_PREV_HASH = ""

    def __init__(self):
        if WriterService.__instance is not None:
            raise Exception("Singleton instance already exists. Use WriterService.get_instance() to get that instance.")
        WriterService.__instance = self

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

    def write(self, block_hash, block):
        file_for_block = block_hash + '.json'

        # createFileCommand = 'hdfs dfs –touchz /BlockChain/' + file_for_block
        # createFileCommand = 'touch ./BlockChain/' + file_for_block
        # subprocess.call(createFileCommand, shell=True)

        block_json = json.dumps(block.convert_to_dict())

        with open('./BlockChain/' + file_for_block, 'w') as f:  # writing JSON object
            f.write(block_json)

        self.head_block = block
