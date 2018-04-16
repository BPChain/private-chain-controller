#!/bin/bash

echo "Creating blockains directory"
if [ ! -d "private-xain" ]; then
	git clone https://github.com/BPChain/private-xain.git -b dev
fi
if [ ! -d "private-multichain" ]; then
	git clone https://github.com/BPChain/private-multichain.git -b dev
fi
if [ ! -d "private-ethereum" ]; then
	git clone https://github.com/BPChain/private-ethereum.git -b dev
fi
./startController.sh