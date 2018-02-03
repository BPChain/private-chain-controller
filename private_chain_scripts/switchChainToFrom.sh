#!/bin/bash
# Switch the active chain to the one supplied via the first parameter

let "chainToSwitchTo=$1"
let "chainToSwitchFrom=$2"

cd /home/jonas.cremerius/bin/private-"$chainToSwitchFrom"/Node || exit
docker-compose down

cd /home/jonas.cremerius/bin/private-"$chainToSwitchTo"/Node || exit
docker-compose up --build
