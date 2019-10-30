import json
import requests

class NetworkService:
    __instance = None

    def __init__(self):
        if NetworkService.__instance is not None:
            raise Exception("Singleton instance already exists. Use NetworkService.get_instance() to get that instance.")
        
        self.neighbours_address = []
        NetworkService.__instance = self

    @staticmethod
    def get_instance():
        if NetworkService.__instance is None:
            return NetworkService()
        return NetworkService.__instance

    def broadcast_block(self, block):
        block_dict = block.convert_to_dict()
        for i in self.neighbours_address:
            url = "http://{}/block".format(i) # TODO: Add a /block endpoint
            requests.post(url, json=block_dict)

    def broadcast_transaction(self, transaction):
        transaction_dict = transaction.convert_to_dict()
        for i in self.neighbours_address:
            url = "http://{}/transaction".format(i)
            requests.post(url, json=transaction_dict)
