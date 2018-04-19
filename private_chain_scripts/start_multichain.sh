#!/bin/bash
# Starts Multichain blockchain

export HOSTNAME
cd private-multichain || exit
docker-compose up --force-recreate -d
echo "start multichaaaaaaain"