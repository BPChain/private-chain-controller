#!/bin/bash
# Makes x Nodes send transactions to the blockchain

cd /home/jonas.cremerius/bin/XAIN-chain/private-xain/Node || exit

let "transaction_Number=$1"
