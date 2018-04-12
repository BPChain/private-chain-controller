#!/bin/bash
# Removes xain

cd /home/"$USER"/bin/private-xain/Node || exit
docker-compose down --remove-orphans
