#!/bin/bash
now=$(date +"%Y-%m-%d  %H:%M:%S")
if [ "$1" == "70069549" ];then
  echo "Time: $now     User: Kwinten">>/etc/openhab2/html/MQTTLogger.txt
elif [ "$1" == "79938499" ];then
  echo "Time: $now     User: Mats">>/etc/openhab2/html/MQTTLogger.txt
elif [ "$1" == "67306243" ];then
  echo "Time: $now     User: Michiel">>/etc/openhab2/html/MQTTLogger.txt
fi

