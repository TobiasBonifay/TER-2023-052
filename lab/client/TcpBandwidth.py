import socket
import subprocess
import time

from lab.Constants import VM2_IP, VM1_IP, INTERFACE
from lab.apache2.TcpMemProc import PORT, HOST
from lab.client.BandwidthMonitor import BandwidthMonitor


def run_apache_benchmark():
    """Run the Apache benchmark and return the mean time per request."""
    command = f"ab -n 100000 -c 500 http://{VM1_IP}/"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()
        # Parse and return the mean time per request from the benchmark result
        for line in output.splitlines():
            if "Time per request:" in line and "[ms] (mean" in line:
                # The line format is expected to be: 'Time per request: [time] [ms] (mean, across all concurrent
                # requests)' Extract the time by splitting by spaces and taking the fourth element
                mean_time_str = line.split()[3]
                # Ensure we only process digits and dot for float conversion
                if all(char.isdigit() or char == '.' for char in mean_time_str):
                    return float(mean_time_str)
        return 0  # If not found, return 0
    except subprocess.CalledProcessError as e:
        print(f"Error while running apache benchmark: {e.stderr.decode()}")
        return 0
    except ValueError as ve:
        print(f"Value error encountered: {ve}")
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
