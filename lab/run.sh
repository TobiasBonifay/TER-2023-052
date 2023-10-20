#!/bin/bash

python3 packet_capture.py &

sleep 2

VM1_IP="192.168.100.10"
httperf --server $VM1_IP --num-conns 1000 --rate 10 --print-reply --log ct_logs.txt

kill %1