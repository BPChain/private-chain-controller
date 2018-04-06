#!/bin/bash

cd /home/"$USER"/bin/private-chain-controller/service || exit
cp -v blockchainController.service /lib/systemd/system/blockchainController.service

sudo chmod 644 /lib/systemd/system/blockchainController.service
sudo systemctl daemon-reload
sudo systemctl enable blockchainController.service
sudo systemctl start blockchainController.service
