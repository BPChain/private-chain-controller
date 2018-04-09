#!/bin/bash

processId=$(ps -ef | grep 'controller.py' | grep -v 'grep' | awk '{ printf $2 }')
kill "$processId"
