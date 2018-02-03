#!/bin/bash
# Makes x Nodes send transactions to the blockchain

cd /home/jonas.cremerius/bin/private-ethereum/Node || exit

let "transaction_Number=$1"
