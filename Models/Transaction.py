#!/usr/bin/python3

import rsa
import codecs
from hashlib import sha256
from random import randint


class Transaction:

    def __init__(self, sender, data, signature):
        self.sender = sender
        self.data = data
        self.signature = signature

    def __str__(self):
        data_hash = sha256(self.data.encode()).hexdigest()
        return "Sender: {} \nData: {}\n".format(self.sender, data_hash)
    
    def get_id(self):
        t = self.sender + self.data + self.signature + str(randint(1, 3000))
        transaction_hash = sha256(t.encode()).hexdigest()
        return transaction_hash

    def verify(self):
        # The 'sender' is the PEM format of the sender's RSA public key
        pubkey = rsa.PublicKey.load_pkcs1(self.sender)
        data_hash = sha256(self.data.encode()).hexdigest()
        signature = codecs.decode(self.signature.encode(), "hex") # hex to bytes conversion

        try:
            rsa.verify(data_hash, signature, pubkey)
            return True
        except rsa.pkcs1.VerificationError:
            return False
