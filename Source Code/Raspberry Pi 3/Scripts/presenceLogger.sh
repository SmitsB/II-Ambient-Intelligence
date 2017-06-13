#!/bin/bash
now=$(date +"%Y-%m-%d  %H:%M:%S")
echo "Time: $now     Presence Detected">>/etc/openhab2/html/presenceLogger.txt

