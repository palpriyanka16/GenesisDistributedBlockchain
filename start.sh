#!/usr/bin/env bash

# remove the blocks generated in the previous session
rm BlockChain/*.json

# start listening
python3 -m TransactionListener
