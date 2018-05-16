#!/bin/bash
echo "Running setup"
if [ ! -d "private-xain" ]; then
	git clone https://github.com/BPChain/private-xain.git -b dev
else
    cd private-xain || exit
    git pull
    cd Node
    docker-compose build --force-rm
    cd .. || exit
    cd .. || exit
fi
if [ ! -d "private-multichain" ]; then
	git clone https://github.com/BPChain/private-multichain.git -b dev
else
    cd private-multichain || exit
    git pull
    docker-compose build --force-rm
    cd .. || exit
fi
if [ ! -d "private-ethereum" ]; then
	git clone https://github.com/BPChain/private-ethereum.git -b dev
else
    cd private-ethereum || exit
    git pull
    docker-compose build --force-rm
    cd .. || exit
fi
export LC_ALL=C
if [ ! -d "virtualenv" ]; then
    echo "Creating virtual python environment..."
	python3 -m venv ./virtualenv
	source virtualenv/bin/activate
    echo "Installing Python requirements"
    pip3 install -r requirements.txt
fi