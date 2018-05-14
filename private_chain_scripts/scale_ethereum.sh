#!/bin/bash
# Scale Etherum nodes to x amount of nodes supplied by first parameter

export HOSTNAME

cd private-ethereum || exit
docker-compose scale eth_node="$1"
