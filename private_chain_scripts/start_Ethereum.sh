#!/bin/bash
# Starts Ethereum blockchain

cd /home/jonas.cremerius/bin/Ethereum/private-ethereum/Node || exit
docker-compose up --build
