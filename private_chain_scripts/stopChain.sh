#!/bin/bash
# Removes Chain supplied by first argument

cd /home/"$USER"/bin/private-"$1"/Node || exit
docker-compose down --remove-orphans
