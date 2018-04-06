#!/bin/bash

cd /home/"$USER"/bin/private-chain-controller|| exit
cp -v blockchainController.service /lib/systemd/system/blockchainController.service

chmod 644 /lib/systemd/system/blockchainController.service
systemctl daemon-reload
systemctl enable blockchainController.service
systemctl start blockchainController.service
