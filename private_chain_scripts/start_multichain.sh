#!/bin/bash
# Starts Multichain blockchain

export HOSTNAME

cd /home/"$USER"/bin/private-multichain || exit
docker-compose up --build
