#!/bin/bash
# Removes ethereum

cd /home/"$USER"/bin/private-ethereum/Node || exit
docker-compose down --remove-orphans
