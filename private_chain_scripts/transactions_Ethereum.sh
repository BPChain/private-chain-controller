#!/bin/bash
# Makes x Nodes send transactions to the blockchain

cd /home/jonas.cremerius/bin/Ethereum/private-ethereum/Node || exit

let "transaction_Number=$1"
