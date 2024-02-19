import argparse
import socket
import subprocess

from lab.common.Constants import VM2_IP, VM1_IP, VM2_PORT

parser = argparse.ArgumentParser(description='Server Test Script')
parser.add_argument('--test-type', choices=['apache', 'locust'], required=True, help='Type of test to run (apache or '
                                                                                     'locust)')
args = parser.parse_args()


def run_apache_benchmark():
    """Run the Apache benchmark and return the mean time per request."""
    command = f"ab -n 20000 -c 1000 http://{VM1_IP}/"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()
        # Parse and return the mean time per request from the benchmark result
        for line in output.splitlines():
            if "Time Taken" in line:
                print(line)
            if "Time per request:" in line and "[ms] (mean" in line:
                # The line format is expected to be: 'Time per request: [time] [ms] (mean, across all concurrent
                # requests)' Extract the time by splitting by spaces and taking the fourth element
                mean_time_str = line.split()[3]
                # Ensure we only process digits and dot for float conversion
                if all(char.isdigit() or char == '.' for char in mean_time_str):
                    return float(mean_time_str)
        return 0.0
    except subprocess.CalledProcessError as e:
        print(f"Error while running apache benchmark: {e.stderr.decode()}")
        return 0
    except ValueError as ve:
        print(f"Value error encountered: {ve}")
        return 0


def run_locust_test():
    # run locust test and take the mean time per request
    command = f"locust -f Locust.py --headless -u 1000 -r 100 --run-time 1m"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()
        # Parse and return the mean time per request from the benchmark result
        for line in output.splitlines():
            if "Average" in line and "Requests/sec" in line:
                # The line format is expected to be: 'Time per request: [time] [ms] (mean, across all concurrent
                # requests)' Extract the time by splitting by spaces and taking the fourth element
                mean_time_str = line.split()[1]
                # Ensure we only process digits and dot for float conversion
                if all(char.isdigit() or char == '.' for char in mean_time_str):
                    return float(mean_time_str)
        return 0  # If not found, return 0
    except subprocess.CalledProcessError as e:
        print(f"Error while running locust test: {e.stderr.decode()}")
        return 0


def run_server(host, port):
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
                        data_to_send = f"{response_time}"
                        conn.sendall(data_to_send.encode())
                        print(f"Sent {data_to_send}")
                except BrokenPipeError as e:
                    print(f"Broken pipe error: {e}")
                    # If the client disconnects, we should continue listening for new connections
                    continue
                finally:
                    conn.close()
                    print(f"Disconnected from {addr}")
        except KeyboardInterrupt:
            print("Server is shutting down.")


if __name__ == "__main__":
    run_server(VM2_IP, VM2_PORT)
