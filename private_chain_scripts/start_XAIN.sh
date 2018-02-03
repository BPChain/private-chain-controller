#!/bin/bash
# Starts XAIN blockchain

cd /home/jonas.cremerius/bin/private-xain/Node || exit
docker-compose up --build
