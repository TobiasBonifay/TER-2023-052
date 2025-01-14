#!/bin/bash
# Script to wget from
# https://raw.githubusercontent.com/TobiasBonifay/TER-2023-052/main/lab/apache2/setup.sh

sudo apt update
sudo apt install apache2 -y
sudo systemctl enable apache2

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
# change the cgroup path to the correct one
ip a
# nano config.json

# sudo python3 -m lab.apache2.MemoryGetterApache