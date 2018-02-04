#!/bin/bash
# Starts XAIN blockchain

cd /home/"$USER"/bin/private-xain/Node || exit
docker-compose up --build
