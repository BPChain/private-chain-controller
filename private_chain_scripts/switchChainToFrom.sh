#!/bin/bash
# Switch the active chain to the one supplied via the first parameter

cd /home/"$USER"/bin/private-"$2"/Node || exit
docker-compose down --remove-orphans

cd /home/"$USER"/bin/private-"$1"/Node || exit
docker-compose up --build
