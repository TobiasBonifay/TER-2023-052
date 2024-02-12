#!/bin/bash
# Script to wget from
# https://raw.githubusercontent.com/TobiasBonifay/TER-2023-052/main/lab/client/setup.sh

sudo apt update
sudo apt install apache2-utils -y

sudo apt install git -y
git clone https://github.com/TobiasBonifay/TER-2023-052.git
cd TER-2023-052/lab/ || exit 1
sudo apt install -y python3-pip

# pip install -r requirements.txt if error continue the script
output=$(pip3 install -r requirements.txt 2>&1)
if [ $? -ne 0 ]; then
    echo "Error: $output"
fi

# ip a and wait user to choose the interface and edit the config.json
ip a
nano config.json

sudo python3 -m lab.client.TcpBandwidth