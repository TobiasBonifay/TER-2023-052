# VM2 Script (Updated with Bandwidth Monitoring)
import socket
import subprocess
import time

from lab.client.BandwidthMonitor import BandwidthMonitor
from lab.config_loader import load_config

config = load_config()

HOST = config['VM2_HOST']  # was 0.0.0.0
PORT = config['VM2_PORT']
APACHE_SERVER_IP = config['VM1_HOST']  # IP of VM1 to target
INTERFACE = config['INTERFACE']  # of the bridge
VM2_IP = config['VM1_HOST']  # itself ip address


def run_apache_benchmark():
    try:
        command = f"ab -n 1000 -c 1 http://{APACHE_SERVER_IP}/"
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()
        for line in output.splitlines():
            if "(longest request)" in line:
                return int(line.split()[2])
    except subprocess.CalledProcessError as e:
        print(f"Error while running apache benchmark: {e.stderr.decode()}")
        return 0


bw_monitor = BandwidthMonitor(INTERFACE, VM2_IP)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"Listening {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    print(f"Connected by {addr}")

    while True:
        response_time = run_apache_benchmark()
        bw_download, bw_upload = bw_monitor.get_bandwidth()
        data_to_send = f"{response_time},{bw_download},{bw_upload}"
        conn.sendall(data_to_send.encode())
        time.sleep(45)

    conn.close()
    print(f"Disconnected from {addr}")
