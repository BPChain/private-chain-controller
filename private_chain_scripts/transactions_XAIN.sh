#!/bin/bash
# Makes x Nodes send transactions to the blockchain

cd /home/"$USER"/bin/private-xain/Node || exit

let "transaction_Number=$1"
