#!/bin/bash
# Removes ethereum

cd private-ethereum/Node || exit
docker-compose down
