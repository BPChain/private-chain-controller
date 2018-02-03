#!/bin/bash
# Makes x Nodes do nothing except listening for propagated blocks and
# perhaps send transactions

cd /home/jonas.cremerius/bin/private-xain/Node || exit

docker-compose scale xain_lazy="$1"
