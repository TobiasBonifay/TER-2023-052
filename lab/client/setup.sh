#!/bin/bash
# Script to wget from
# https://raw.githubusercontent.com/TobiasBonifay/TER-2023-052/main/lab/client/setup.sh

sudo apt update
sudo apt install apache2-utils -y

sudo apt install git -y
git clone https://github.com/TobiasBonifay/TER-2023-052.git
cd TER-2023-052/lab/ || exit 1
sudo apt install -y python3-pip
pip3 install -r requirements.txt
sudo python3 -m lab.client.TcpBandwidth