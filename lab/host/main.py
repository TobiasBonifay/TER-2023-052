import csv
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
MODEL_PATH = 'saved_model.pb'


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


def parse_memory_info(meminfo):
    # Sample implementation - adjust based on your actual meminfo format
    lines = meminfo.split('\n')
    mem_total = mem_free = 0
    for line in lines:
        if 'MemTotal' in line:
            mem_total = int(line.split()[1])  # Assuming second column is the value
        elif 'MemFree' in line:
            mem_free = int(line.split()[1])

    mem_used = mem_total - mem_free
    return mem_used


def get_vm_memory_usage(client):
    memory_info = client.get_data()
    parsed_memory_info = parse_memory_info(memory_info)
    return parsed_memory_info


def get_response_time(client):
    response_time = float(client.get_data())
    return response_time


def load_model():
    return tf.keras.models.load_model(MODEL_PATH)


def main():
    client_vm1 = Client(VM1_HOST, VM1_PORT)
    client_vm2 = Client(VM2_HOST, VM2_PORT)
    model = load_model()

    with open('vm_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Memory (VM view)', 'Memory (Host view)', 'CT', 'BW (Download)', 'BW (Upload)'])

        try:
            for _ in range(DURATION):
                current_time = time.time()  # Epoch time

                vm_memory_usage = get_vm_memory_usage(client_vm1)
                response_time = get_response_time(client_vm2)

                # Assuming bandwidth data is available, replace these with actual values
                bw_download = 0  # Placeholder for download bandwidth
                bw_upload = 0  # Placeholder for upload bandwidth

                # Write data to CSV
                writer.writerow(
                    [current_time, vm_memory_usage, 'Memory_Host_View', response_time, bw_download, bw_upload])

                # Prepare data for model inference
                data_for_inference = np.array([[vm_memory_usage, response_time]])
                predicted_value = model.predict(data_for_inference)

                # Logic to adjust cgroup based on the prediction

                time.sleep(FINESSE)
        finally:
            client_vm1.close()
            client_vm2.close()


if __name__ == "__main__":
    main()
