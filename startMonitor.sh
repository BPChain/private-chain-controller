#!/bin/bash
echo "Activating virtual python environment..."
source virtualenv/bin/activate
echo "Starting Monitor"
python3 monitor.py || exit
