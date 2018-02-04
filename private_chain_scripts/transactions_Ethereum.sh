#!/bin/bash
# Makes x Nodes send transactions to the blockchain

cd /home/"$USER"/bin/private-ethereum/Node || exit

let "transaction_Number=$1"
