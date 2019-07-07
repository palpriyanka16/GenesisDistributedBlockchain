#!/usr/bin/env bash

# remove the blocks generated in the previous session
rm BlockChain/*.json
rm BlockChain/head_block_hash

# start listening
python3 -m TransactionListener
