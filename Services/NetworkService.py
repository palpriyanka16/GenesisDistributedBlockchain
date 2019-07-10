#!/usr/bin/python3

import requests


class NetworkService:
    __instance = None

    PEERS_ADDRESS = []

    def __init__(self):
        if NetworkService.__instance is not None:
            raise Exception("Singleton instance already exists. Use NetworkService.get_instance() to get that instance.")
        NetworkService.__instance = self

    @staticmethod
    def get_instance():
        if NetworkService.__instance is None:
            return NetworkService()
        return NetworkService.__instance

    #function to send the block to peers of the current node
    def forward_block_json_to_peers(self, block_json):

        # TODO: Need to find a way to just send a request and not care about the response
        # at all. The below commented hack works but throws certain response related
        # exceptions
        #
        #
        # for peer_address in self.PEERS_ADDRESS:
        #     try:
        #         rs = requests.post(url = peer_address, data = {'block_data': block_json}, timeout = 0.00001)
        #     except requests.exceptions.ReadTimeout: #this confirms you that the request has reached server
        #         pass
        #
        #
        # The need for above solution is because, if a cycle of requests form in the network
        # there will be a deadlock with each node in the cycle waiting for the next node to return
        # a response. The below code WILL ONLY WORK in deadlock free scenarios. Replace the code below
        # with the code snippet in the comment to see the working!
        for peer_address in self.PEERS_ADDRESS:
            rs = requests.post(url = peer_address, data = {'block_data': block_json})
