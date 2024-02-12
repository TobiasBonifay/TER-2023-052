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
pip3 install -r requirements.txt
sudo python3 -m lab.apache2.TcpMemProc