#!/bin/bash
# Starts Multichain blockchain

export HOSTNAME
cd private-multichain || exit
docker-compose up --build