#!/bin/bash

processId=$(ps -ef | grep 'status_monitor.py' | grep -v 'grep' | awk '{ printf $2 }')
kill "$processId"
