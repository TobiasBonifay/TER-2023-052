# main.py - Host Script
import socket
import time
import numpy as np
import tensorflow as tf
from threading import Thread

# Constants and configurations
VM1_HOST = 'VM1_IP_ADDRESS'
VM1_PORT = 8000
VM2_HOST = 'VM2_IP_ADDRESS'
VM2_PORT = 8001
DURATION = 99999
FINESSE = 0.5
TIME_RESPONSE = 0
THRESHOLD = 500


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))

    def get_data(self):
        self.client.send(b"GET")
        data = self.client.recv(4096)
        return data.decode()

    def close(self):
        self.client.close()


def get_vm_memory_usage(client):
    memory_info = client.get_data()
    # Parse memory info to extract desired metrics
    # ... parsing logic here ...
    return parsed_memory_info


def get_response_time(client):
    response_time = client.get_data()
    return response_time


def main():
    client_vm1 = Client(VM1_HOST, VM1_PORT)
    client_vm2 = Client(VM2_HOST, VM2_PORT)

    try:
        for _ in range(DURATION):
            vm_memory_usage = get_vm_memory_usage(client_vm1)
            response_time = get_response_time(client_vm2)
            # Additional logic to process and store data, perform inference, adjust cgroups, etc.
            # ...

            time.sleep(FINESSE)
    finally:
        client_vm1.close()
        client_vm2.close()


if __name__ == "__main__":
    main()
