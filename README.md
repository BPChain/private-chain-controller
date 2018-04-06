# private-chain-controller

# Check status
sudo systemctl status blockchainController.service

# Start service
sudo systemctl start blockchainController.service

# Stop service
sudo systemctl stop blockchainController.service

# Check service's log
sudo journalctl -f -u blockchainController.service
