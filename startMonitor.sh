#!/bin/bash
echo "Starting Monitor"
echo "Activating virtual python environment..."
source virtualenv/bin/activate
python3 status_monitor.py || exit
