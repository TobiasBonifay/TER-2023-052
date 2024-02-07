import socket
import subprocess
import time

from lab.client.BandwidthMonitor import BandwidthMonitor
from lab.config_loader import load_config

# Load configuration
config = load_config()
HOST = config['VM2_HOST']
PORT = config['VM2_PORT']
APACHE_SERVER_IP = config['VM1_HOST']  # IP of VM1 to target for the benchmark
INTERFACE = config['INTERFACE']  # Network interface for bandwidth monitoring
VM2_IP = config['VM2_IP']  # The IP address of this VM


def run_apache_benchmark():
    """Run the Apache benchmark and return the longest request time."""
    command = f"ab -n 1000 -c 1 http://{APACHE_SERVER_IP}/"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()
        # Parse and return the longest request time from the benchmark result
        return next((int(line.split()[2]) for line in output.splitlines() if "(longest request)" in line), 0)
    except subprocess.CalledProcessError as e:
        print(f"Error while running apache benchmark: {e.stderr.decode()}")
        return 0


def run_server(host, port, bandwidth_monitor):
    """Run the TCP server to send bandwidth measurements to the client."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()
        print(f"Listening on {host}:{port}")

        try:
            while True:
                conn, addr = server.accept()
                print(f"Connected by {addr}")

                try:
                    while True:
                        response_time = run_apache_benchmark()
                        bw_download, bw_upload = bandwidth_monitor.get_bandwidth()
                        data_to_send = f"{response_time},{bw_download},{bw_upload}"
                        conn.sendall(data_to_send.encode())
                        time.sleep(45)
                finally:
                    conn.close()
                    print(f"Disconnected from {addr}")
        except KeyboardInterrupt:
            print("Server is shutting down.")


if __name__ == "__main__":
    bw_monitor = BandwidthMonitor(INTERFACE, VM2_IP)
    run_server(HOST, PORT, bw_monitor)
