#!/usr/bin/python3

import requests
import json

class NetworkService:
    __instance = None

    PEERS_ADDRESS = []     # list of "host:port"

    def __init__(self):
        if NetworkService.__instance is not None:
            raise Exception("Singleton instance already exists. Use NetworkService.get_instance() to get that instance.")
        NetworkService.__instance = self

    @staticmethod
    def get_instance():
        if NetworkService.__instance is None:
            return NetworkService()
        return NetworkService.__instance
    
    def broadcast_block(self, block):
        '''
            Function to send a mined block to peers of the current node
        '''
        block_dict = block.convert_to_dict()
        for i in self.PEERS_ADDRESS:
            url = "http://{}/block".format(i)
            requests.post(url=url, data={'block_data': json.dumps(block_dict)})
