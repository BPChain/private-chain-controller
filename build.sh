#!/bin/bash
echo "Running setup"
if [ ! -d "private-xain" ]; then
	git clone https://github.com/BPChain/private-xain.git -b dev
fi
if [ ! -f "Node/files/geth" ]; then
    echo "You need to provide Xain-Geth binary. Xain will not be build!!!!!!"
else
    cd private-xain || exit
    git pull || exit 1
    cd Node || exit 1
    docker-compose build --force-rm
    cd ../..
fi
if [ ! -d "private-multichain" ]; then
	git clone https://github.com/BPChain/private-multichain.git -b dev
fi
cd private-multichain || exit 1
git pull || exit 1
docker-compose build --force-rm
cd ..
if [ ! -d "private-ethereum" ]; then
	git clone https://github.com/BPChain/private-ethereum.git -b dev
fi
cd private-ethereum || exit 1
git pull || exit 1
docker-compose build --force-rm
cd ..
export LC_ALL=C
if [ ! -d "virtualenv" ]; then
    echo "Creating virtual python environment..."
	python3 -m venv ./virtualenv || exit 1
fi
source virtualenv/bin/activate || exit 1
echo "Installing Python requirements"
pip3 install -r requirements.txt || exit 1
echo "Done installing"