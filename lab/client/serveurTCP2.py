# VM2 Script (Updated with Bandwidth Monitoring)
import socket
import subprocess
import time
import pcapy
from threading import Thread, Lock

HOST = '0.0.0.0'
PORT = 8001
APACHE_SERVER_IP = '192.168.100.231'
INTERFACE = 'virbr10'


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


class BandwidthMonitor:
    def __init__(self, interface):
        self.interface = interface
        self.bw_download = 0
        self.bw_upload = 0
        self.lock = Lock()
        Thread(target=self.monitor_bandwidth).start()

    def monitor_bandwidth(self):
        pcap = pcapy.open_live(self.interface, 65536, 1, 0)
        while True:
            header, packet = pcap.next()
            packet_length = len(packet)
            # TODO: Distinguish between download and upload
            with self.lock:
                self.bw_download += packet_length
                self.bw_upload += packet_length

    def get_bandwidth(self):
        with self.lock:
            bw_download = self.bw_download
            bw_upload = self.bw_upload
            self.bw_download = 0
            self.bw_upload = 0
        return bw_download, bw_upload


bw_monitor = BandwidthMonitor(INTERFACE)

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
