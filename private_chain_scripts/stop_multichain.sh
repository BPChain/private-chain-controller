#!/bin/bash
# Removes multichain

cd private-multichain || exit
docker-compose down --remove-orphans
