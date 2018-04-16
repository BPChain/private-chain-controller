#!/bin/bash
# Starts XAIN blockchain

export HOSTNAME

cd private-xain/Node || exit
docker-compose up --build
