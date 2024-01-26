import socket
import subprocess
import time
import re
"""This TCP server is in the client (VM2) and is used to communicate with the host (this PC) the response time of the 
apache server every 45s"""

HOST = '0.0.0.0'
PORT = 8001
APACHE_SERVER_IP = '192.168.100.231'


def run_apache_benchmark():
    try:
        command = f"ab -n 1000 -c 1 http://{APACHE_SERVER_IP}/"
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode()

        # Extract the longest request time?
        match = re.search(r"\d+\.\d+", output)
        longest_request_time = match.group(0) if match else "0"
        return longest_request_time
    except subprocess.CalledProcessError as e:
        print(f"Apache benchmark failed: {e.stderr}")
        return "error"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"Listening {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    print(f"Connected by {addr}")

    while True:
        response_time = run_apache_benchmark()
        conn.sendall(response_time.encode())
        time.sleep(45)

    conn.close()
    print(f"Disconnected from {addr}")
