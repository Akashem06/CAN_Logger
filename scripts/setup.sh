#!/bin/bash

log_file=/home/midnightsun/Documents/$(date '+%d-%m-%Y_%H-%M').log
touch $log_file
python3 /home/midnightsun/Downloads/telemMSXV/utils/can_log.py > $log_file
