#!/bin/bash
# Scale Etherum nodes to x amount of nodes supplied by first parameter

cd /home/"$USER"/bin/private-ethereum/Node || exit
docker-compose scale eth_node="$1"
