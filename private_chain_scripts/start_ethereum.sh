#!/bin/bash
# Starts Ethereum blockchain

cd /home/"$USER"/bin/private-ethereum/Node || exit
docker-compose up --build
