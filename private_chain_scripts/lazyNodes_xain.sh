#!/bin/bash
# Makes x Nodes do nothing except listening for propagated blocks and
# perhaps send transactions

export HOSTNAME

cd private-xain/Node || exit

docker-compose scale xain_lazy="$1"
