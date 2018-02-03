#!/bin/bash
# Makes x Nodes do nothing except listening for propagated blocks and
# perhaps send transactions

cd /home/jonas.cremerius/bin/private-ethereum/Node || exit

docker-compose scale eth_lazy="$1"
