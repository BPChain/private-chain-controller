#!/bin/bash
echo "Creating blockains directory"
python3 -m venv ./virtualenv
source virtualenv/bin/activate
pip3 install -r requirements.txt 
if [ ! -d "private-xain" ]; then
	git clone https://github.com/BPChain/private-xain.git -b dev
else
    cd private-xain
    git pull
    cd ..
fi
if [ ! -d "private-multichain" ]; then
	git clone https://github.com/BPChain/private-multichain.git -b dev
else
    cd private-multichain
    git pull
    cd ..
fi
if [ ! -d "private-ethereum" ]; then
	git clone https://github.com/BPChain/private-ethereum.git -b dev
else
    cd private-ethereum
    git pull
    cd ..
fi

./startController.sh
