#!/usr/bin/python3

import requests
import json
import logging
logging.basicConfig(level=logging.DEBUG)

class NetworkService:
    __instance = None

    PEERS_ADDRESS = []     # list of "host:port" e.g. "194.56.23.57:5000"

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
            logging.info("Sending block to " + url)
            requests.post(url=url, json=block_dict)

    def broadcast_transaction(self, transaction):
        '''
            Function to send a new transaction to peers of the current node
        '''
        transaction_dict = transaction.convert_to_dict()
        for i in self.PEERS_ADDRESS:
            url = "http://{}/transaction".format(i)
            logging.info("Sending transaction to " + url)
            requests.post(url, data=transaction_dict)
