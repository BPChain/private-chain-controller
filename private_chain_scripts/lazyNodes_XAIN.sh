#!/bin/bash
# Makes x Nodes do nothing except listening for propagating  blocks and
# perhaps send transactions

cd /home/jonas.cremerius/bin/XAIN-chain/private-xain/Node || exit

let "lazy_Number=$1"
