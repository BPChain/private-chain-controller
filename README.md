# private-chain-controller
The Private Chain Controller is used to start, stop, and scale blockchain nodes. It also sends 
scenario settings to the [`scenario-orchestrators`](https://github.com/BPChain/scenario-orchestration-service)
running in the different blockchain networks. This project also contains a 
[`monitor`](monitor.py) script which informs the 
[`api-server`](https://github.com/BPChain/api-server) about the blockchains currently running.

### Requirements 
You should have at least:
- docker 1.13.1
- docker-compose 1.8.0
- Python 3.5.2 with pip3
### Usage 
This project contains the files needed to build a blockchain backend. 
1. Run `./build.sh`
to download the blockchains, create the virtual environment, and install the requirements for the
 [`controller`](controller.py) and [`monitor`](monitor.py).
2. Run `./runAll.sh` to run the `controller` and `monitor`. The `controller` will connect to the 
`api-server` and wait for its input. 
3. To stop `controller` and `monitor` run `./killAll.sh` this will also remove all 
docker-containers of blockchains that have been started. 

### Extending 
The controller is meant to be extendable. Configuration details for new chains can be added in the 
[`config`](config.yaml) file. You can also change the address of the `api-server` there. Build 
details would have to be added in the `build.sh` script. 