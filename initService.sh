#!/bin/bash

cd /home/"$USER"/bin/private-chain-controller|| exit
cp -v blockchainController.service /lib/systemd/system/blockchainController.service
