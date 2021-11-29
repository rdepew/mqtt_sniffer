#!/bin/sh

echo ===== install-mqtt_sniffer.sh: Specify a broker =====
echo Enter the IP address of the MQTT broker.
echo This is optional. If you enter an IP address, the installer 
echo will run MQTT listener when installation is complete.
echo "IP address: \c"
read BROKER_IP
if [ $BROKER_IP ]
then
  echo ===== install-mqtt_sniffer.sh: Specify a nodename =====
  echo Enter the name of the node you wish to follow.
  echo This is optional. If you enter a nodename, MQTT listener
  echo will only listen for MQTT topics with that nodename.
  echo If you do not enter a nodename, MQTT listener will
  echo listen for all MQTT topics on the MQTT broker.
  echo "Nodename: \c"
  read NODENAME
fi

echo ===== install-mqtt_sniffer.sh: Installing dependencies =====
sudo apt update -y
sudo apt install -y python3-pip python3-protobuf
pip3 install paho-mqtt
if [ $? -ne 0 ]
then
  echo ===== install-mqtt_sniffer.sh FAIL: Could not install dependencies =====
  exit 1
fi
echo ===== install-mqtt_sniffer.sh: Dependencies successfully installed =====

if [ $BROKER_IP ]
then
  echo ===== install-mqtt_sniffer.sh: Starting MQTT Listener =====
  if [ $NODENAME ]
  then
    echo ">" python3 mqtt_sniffer.py -i $BROKER_IP -N $NODENAME
    python3 mqtt_sniffer.py -i $BROKER_IP -N $NODENAME
  else
    echo ">" python3 mqtt_sniffer.py -i $BROKER_IP
    python3 mqtt_sniffer.py -i $BROKER_IP
  fi
else
  echo ===== install-mqtt_sniffer.sh: Installation completed =====
  echo Execute \`python3 mqtt_sniffer.py -i \<your-ip-address-here\>\`
  echo to run.
  echo Execute \`python3 mqtt_sniffer.py --help\' to view the Help message.
fi
