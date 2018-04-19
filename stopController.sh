#!/bin/bash
echo "Stopping controller and blockchains"
processId=$(ps -ef | grep 'controller.py' | grep -v 'grep' | awk '{ printf $2 }')
kill "$processId"
