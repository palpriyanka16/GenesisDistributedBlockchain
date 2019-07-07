#!/usr/bin/env bash

# Check for flags in the start command
while [ ! $# -eq 0 ]; do
	case "$1" in
		# When --reset flag is passed, clear the existing Blockchain
		--reset)
			# remove the blocks generated in the previous session
			rm BlockChain/*.json
			rm BlockChain/head_block_hash
			;;
	esac
	shift
done

# start listening
python3 -m TransactionListener
