#!/bin/bash
# Removes ethereum

cd private-ethereum || exit
docker-compose down
