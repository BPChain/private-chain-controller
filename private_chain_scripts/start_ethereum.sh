#!/bin/bash
# Starts Ethereum blockchain

export HOSTNAME

cd private-ethereum/Node || exit
docker-compose up --build --force-recreate -d
