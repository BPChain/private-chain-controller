#!/bin/bash
# Scale to x nodes supplied as fist parameter

cd /home/jonas.cremerius/bin/XAIN-chain/private-xain/Node || exit

let "scale_number=0"
let "scale_count=0"
let "scale_to_number=$1"

current_number=$(docker ps -aq --filter name=xain_node --format '{{.Image}}' | wc -l)


if [ "$scale_to_number" -ge 0 ] && [ "$scale_to_number" -lt "$current_number" ]
then
    echo "scaling down to $scale_to_number nodes from $current_number nodes"
    while [ "$scale_to_number" -lt "$current_number" ]
    do
        scale_number=$(docker ps -aq --filter name=xain_node --format '{{.Image}}' | wc -l | awk '{print $1%6}')
        scale_number=$(((scale_number-1) % 6))

        scale_count=$(docker ps -aq --filter name=xain_node_$scale_number --format '{{.Image}}' | wc -l)
        scale_count=$((scale_count-1))

        if [ "$scale_count" -ge 0 ] && [ "$scale_number" -ge 0 ] && [ "$scale_number" -le 5 ]
        then
            docker-compose scale xain_node_$scale_number=$scale_count
        fi
        current_number=$(docker ps -aq --filter name=xain_node --format '{{.Image}}' | wc -l)
        echo "reached $current_number nodes..."
    done
    echo "done."
elif [ "$scale_to_number" -ge 0 ] && [ "$scale_to_number" -gt "$current_number" ]
then
    echo "scaling up to $scale_to_number nodesfrom $current_number nodes"
    while [ "$scale_to_number" -gt "$current_number" ]
    do
        scale_number=$(docker ps -aq --filter name=xain_node --format '{{.Image}}' | wc -l | awk '{print $1%6}')
        scale_count=$(docker ps -aq --filter name=xain_node_$scale_number --format '{{.Image}}' | wc -l)
        scale_count=$((scale_count+1))

        if [ "$scale_count" -ge 0 ] && [ "$scale_number" -ge 0 ] && [ "$scale_number" -le 5 ]
        then
            docker-compose scale xain_node_$scale_number=$scale_count
        fi
        current_number=$(docker ps -aq --filter name=xain_node --format '{{.Image}}' | wc -l)
        echo "reached $current_number nodes..."
    done
    echo "done."
else
    echo "can't scale to $scale_to_number nodes from $current_number nodes"
fi
