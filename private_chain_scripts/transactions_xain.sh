#!/bin/bash
# Makes x Nodes send transactions to the blockchain

cd private-xain/Node || exit

let "transaction_Number=$1"
