import socket
import subprocess

from lab.config_loader import load_config

config = load_config()
HOST = config['VM1_HOST']  # was 0.0.0.0
PORT = config['VM1_PORT']

"""
This TCP server is used to get the memory info from the VM and send it to the client (VM 1)
"""


def get_memory_info():
    meminfo = subprocess.check_output(['cat', '/proc/meminfo']).decode()
    return meminfo


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"Listening {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    print(f"Connected by {addr}")

    while True:
        data = conn.recv(1024)
        if not data:
            break
        response = get_memory_info()
        conn.sendall(response.encode())

    conn.close()
    print(f"Disconnected from {addr}")
