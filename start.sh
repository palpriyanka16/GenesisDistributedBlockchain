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

PORT=8000
NUM_THREADS=3
NUM_WORKERS=1

gunicorn -w $NUM_WORKERS --threads $NUM_THREADS -b 0.0.0.0:$PORT TransactionListener:api \
		 --reload --capture-output --reuse-port --timeout 90
