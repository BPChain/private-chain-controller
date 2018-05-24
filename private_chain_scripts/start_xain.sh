#!/bin/bash
# Starts XAIN blockchain

export HOSTNAME

cd private-xain || exit
docker-compose up --force-recreate -d
