#!/bin/bash
# Starts XAIN blockchain

cd /home/jonas.cremerius/bin/XAIN-chain/private-xain/Node || exit
docker-compose up --build
