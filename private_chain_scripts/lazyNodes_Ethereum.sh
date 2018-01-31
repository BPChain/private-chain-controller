#!/bin/bash
# Makes x Nodes do nothing except listening for propagating  blocks and
# perhaps send transactions

cd /home/jonas.cremerius/bin/Ethereum/private-ethereum/Node || exit

let "lazy_Number=$1"
