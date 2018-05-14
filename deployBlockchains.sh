#!/bin/bash
echo "Running setup"
which git
if [ ! -d "private-xain" ]; then
	git clone https://github.com/BPChain/private-xain.git -b dev
else
    cd private-xain || exit
    git pull
    cd .. || exit
fi
if [ ! -d "private-multichain" ]; then
	git clone https://github.com/BPChain/private-multichain.git -b sub_modules
else
    cd private-multichain || exit
    git pull
    cd .. || exit
fi
if [ ! -d "private-ethereum" ]; then
	git clone https://github.com/BPChain/private-ethereum.git -b scylla_with_pip
else
    cd private-ethereum || exit
    git pull
    cd .. || exit
fi
export LC_ALL=C
if [ ! -d "virtualenv" ]; then
    echo "Creating virtual python environment..."
	python3 -m venv ./virtualenv
fi
echo "Activating virtual python environment..."
source virtualenv/bin/activate
echo "Installing Python requirements"
pip3 install -r requirements.txt
echo "Downloading and updating Blockchains"
echo "Starting Controller"
python3 controller.py || exit