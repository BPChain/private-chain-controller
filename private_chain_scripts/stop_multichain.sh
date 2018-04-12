#!/bin/bash
# Removes multichain

cd /home/"$USER"/bin/private-multichain || exit
docker-compose down --remove-orphans
