import csv
import socket
import time
import numpy as np
import tensorflow as tf

# Constants and configurations
VM1_HOST = '192.168.100.175'  # IP of VM1
VM2_HOST = '192.168.100.231'  # IP of VM2
VM1_PORT = 8000
VM2_PORT = 8001
DURATION = 99999
FINESSE = 0.5
MODEL_PATH = 'saved_model.pb'


# Client class to interact with VMs
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


# Function to parse memory info
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


# Function to load TensorFlow model
def load_model():
    return tf.keras.models.load_model(MODEL_PATH)

# Function to get bandwidth data
def get_bandwidth_data():
    # Implement bandwidth monitoring logic here
    return bw_download, bw_upload

# Main function
def main():
    client_vm1 = Client(VM1_HOST, VM1_PORT)
    client_vm2 = Client(VM2_HOST, VM2_PORT)
    model = load_model()

    with open('vm_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Memory (VM view)', 'Memory (Host view)', 'CT', 'BW (Download)', 'BW (Upload)'])

        for _ in range(DURATION):
            current_time = time.time()
            mem_vm_view, mem_host_view = parse_memory_info(client_vm1.get_data())
            ct = float(client_vm2.get_data())
            bw_download, bw_upload = get_bandwidth_data()

            # Write data to CSV
            writer.writerow([current_time, mem_vm_view, mem_host_view, ct, bw_download, bw_upload])

            # Model inference and cgroup adjustments
            data_for_inference = np.array([[mem_vm_view, ct, bw_download, bw_upload]])
            predicted_value = model.predict(data_for_inference)
            # Adjust cgroup based on predicted_value


            time.sleep(FINESSE)

        client_vm1.close()
        client_vm2.close()


if __name__ == "__main__":
    main()
