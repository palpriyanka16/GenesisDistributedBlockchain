# GenesisDistributedBlockchain

## Description

This repository contains a group of backend services and a web interface to make use of the services to add transactions, view transactions and view the entire blockchain which is being stored as a set of files with each file corresponding to a block. The services will be run on distributed storage like Hadoop to distribute the blockchain across multiple servers.

## Getting started

First, get this project cloned to your local system using the following command on your terminal.

```bash
   git clone https://github.com/palpriyanka16/GenesisDistributedBlockchain.git
```

### Prerequisites

* Install python3 using the following command in Linux terminal
   ```bash
      sudo apt-get update
      sudo apt-get install python3.6  
    ```

* Install pip3 using the following command in Linux terminal
   ```bash
      sudo apt-get install python3-pip
   ```
### Running the project

* Install all the dependencies in python with the help of the following command on your terminal

  ```bash
   pip3 install -r requirements.txt
  ```

* Run the backend services by running the following command on your terminal

  ```bash
     ./start.sh
  ```

* Open index.html in your browser to make use of the web interface in order to avail the different features provided by the backend services.


## Features

* Adding transactions to the blockchain by submitting details like sender, data and signature

   Route: `POST` [/transaction]()
 
   Request: 
    
   ```json
      { 
        "sender": "<sender_name>",
        "data": "<transaction_data>",
        "signature": "<digital_signature>"
      }
   ```
   Response:

   ```json
      { 
        "status": "<response_status>",
      }
   ```
* Retrieving any transaction from the blockchain by submitting details like blockhash and transaction hash of the respective transaction

   Route: `GET` [/transaction]()
 
   Request: 
    
   ```json
      { 
        "txHash": "<transaction_hash>",
        "blockHash": "<block_hash>"
      }
   ```
   Response:

   ```json
      { 
        "status": "success", 
        "data": {
           "sender": "<sender_name>",
           "data": "<transaction_data>",
           "signature": "<digital_signature>"
        }
      }
   ```
* Retrieving the entire blockchain with all the blocks and transactions in each block

   Route: `GET` [/block/all]()
 
   Response:

   ```json
      { 
        "status": "<response_status>",
        "data": [
          { "block_hash": "<block_hash>",
            "block_number": "<block_number>",
            "nonce": "<nonce>","prev_block_hash": 
            "<previous_block_hash>",
            "​​​transactions": {
                "<txOneHash>": {
                  "sender": "<sender_name>",
                  "data": "<transaction_data>",
                  "signature": "<digital_signature>"
                },
                "<txTwoHash>": {
                  "sender": "<sender_name>",
                  "data": "<transaction_data>",
                  "signature": "<digital_signature>"
                }
            }
          },
          { "block_hash": "<block_hash>",
            "block_number": "<block_number>",
            "nonce": "<nonce>","prev_block_hash": 
            "<previous_block_hash>",
            "​​​transactions": {
                "<txOneHash>": {
                  "sender": "<sender_name>",
                  "data": "<transaction_data>",
                  "signature": "<digital_signature>"
                },
                "<txTwoHash>": {
                  "sender": "<sender_name>",
                  "data": "<transaction_data>",
                  "signature": "<digital_signature>"
                }
            }
          }
        ]
      }
   ```

## Built with

* Python
* Html
* Javascript
* CSS

