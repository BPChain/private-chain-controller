#!/bin/bash
# Scale Etherum nodes to x amount of nodes supplied by first parameter

export HOSTNAME

cd /home/"$USER"/bin/private-multichain || exit
docker-compose scale slavenode="$1"
