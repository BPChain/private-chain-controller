#!/bin/bash

processId=$(ps -ef | grep 'monitor.py' | grep -v 'grep' | awk '{ printf $2 }')
kill "$processId"
