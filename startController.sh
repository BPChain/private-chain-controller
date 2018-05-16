#!/bin/bash
echo "Activating virtual python environment..."
source virtualenv/bin/activate
echo "Starting Controller"
python3 controller.py || exit