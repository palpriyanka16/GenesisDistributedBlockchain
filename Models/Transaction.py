#!/usr/bin/python3

import rsa
import codecs
from hashlib import sha256
from random import randint


class Transaction:

    def __init__(self, sender, data, signature):
        self.sender = sender.strip()
        self.data = data
        self.signature = signature.strip()

    def __str__(self):
        data_hash = sha256(self.data.encode()).hexdigest()
        return "Sender: {} \nData: {}\n".format(self.sender, data_hash)
    
    def get_id(self):
        t = self.sender + self.data + self.signature
        transaction_hash = sha256(t.encode()).hexdigest()
        return transaction_hash

    def verify(self):
        # TODO: lol
        return True
        '''
            WARNING: Disabling the cryptographic verification of a transaction
            for developmental purposes only.
            TODO: Enable this function before final submission.
        '''

        # The 'sender' is the PEM format of the sender's RSA public key
        sender_public_key = "-----BEGIN RSA PUBLIC KEY-----\n{}\n-----END RSA PUBLIC KEY-----\n".format(self.sender).encode()
        # sender_public_key = self.sender.encode()
        # print(sender_public_key)
        pubkey = rsa.PublicKey.load_pkcs1(sender_public_key)
        data_hash = sha256(self.data.encode()).hexdigest().encode()
        signature = codecs.decode(self.signature.encode(), "hex") # hex to bytes conversion

        try:
            rsa.verify(data_hash, signature, pubkey)
            return True
        except rsa.pkcs1.VerificationError:
            return False

    def convert_to_dict(self):
        t = {}
        t['sender'] = self.sender
        t['data'] = self.data
        t['signature'] = self.signature
        return t
