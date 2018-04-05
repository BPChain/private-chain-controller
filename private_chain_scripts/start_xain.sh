#!/bin/bash
# Starts XAIN blockchain

export HOSTNAME

cd /home/"$USER"/bin/private-xain/Node || exit
docker-compose up --build
