#!/bin/bash
# Starts Ethereum blockchain

export HOSTNAME

cd /home/"$USER"/bin/private-ethereum/Node || exit
docker-compose up --build
