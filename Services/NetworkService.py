#!/usr/bin/python3

import requests
import json
import logging
logging.basicConfig(level=logging.DEBUG)

from Models import Block


class NetworkService:
    __instance = None

    PEERS_ADDRESS = []     # list of "host:port" e.g. "194.56.23.57:5000"
    my_address = "localhost:8000"       # TODO: Fetch this address from config file
    config = None

    def __init__(self):
        if NetworkService.__instance is not None:
            raise Exception("Singleton instance already exists. Use NetworkService.get_instance() to get that instance.")
        NetworkService.__instance = self

        with open('./config.json', 'r') as f:
            self.config = json.load(f)
        self.my_address = self.config['MY_ADDRESS']

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
        data = {
            "sender": self.my_address,
            "block": block_dict
        }
        for i in self.PEERS_ADDRESS:
            url = "http://{}/block".format(i)
            logging.info("Sending block to " + url)
            requests.post(url=url, json=data)

    def broadcast_transaction(self, transaction):
        '''
            Function to send a new transaction to peers of the current node
        '''
        transaction_dict = transaction.convert_to_dict()
        for i in self.PEERS_ADDRESS:
            url = "http://{}/transaction".format(i)
            logging.info("Sending transaction to " + url)
            requests.post(url, data=transaction_dict)

    def fetch_blockchain_from(self, target_peer):
        url = "http://{}/block/all".format(target_peer)
        logging.info("Fetching blockchain from " + url)
        response = requests.get(url=url)
        blockchain_json = response.json()['data']

        blockchain = []
        for block_json in blockchain_json:
            block = Block.load_from_json(block_json)
            blockchain.append(block)

        return blockchain

    def send_block_for_mining(self, target_node, data):
        url = "http://{}/block/mine".format(target_node)
        logging.info("Sending block for mining to " + url)

        try:
            requests.post(url=url, json=data, timeout=1)
        except requests.exceptions.ReadTimeout:
            pass

    def send_nonce_details_to_master(self, block_hash, nonce_found, nonce, master_address):
        url = "http://{}/block/nonce".format(master_address)
        data = {
            "sender": self.my_address,
            "block_hash": block_hash,
            "nonce_found": nonce_found,
            "nonce": nonce
        }

        try:
            requests.post(url=url, json=data, timeout=1)
        except requests.exceptions.ReadTimeout:
            pass

    def send_valid_nonce_to_master(self, nonce, block_hash, master_address):
        logging.info(self.my_address + ": Nonce with " + str(nonce) + "and block_hash " + block_hash + " will be sent to master.")
        self.send_nonce_details_to_master(block_hash, True, nonce, master_address)

    def inform_master_nonce_not_in_range(self, block_hash, master_address):
        logging.info(self.my_address + ": Nonce not in range will be informed to master.")
        self.send_nonce_details_to_master(block_hash, False, -1, master_address)