import csv
import re
import socket
import time
import numpy as np
import tensorflow as tf

# Constants and configurations
VM1_PATH_CGROUP_FILE = "/sys/fs/cgroup/machine.slice/machine-qemu\\x2d6\\x2dubuntu22.04.scope/memory.max"
VM1_HOST = '192.168.100.175'  # IP of VM1
VM2_HOST = '192.168.100.231'  # IP of VM2
VM1_PORT = 8000
VM2_PORT = 8000
DURATION = 99999
FINESSE = 0.5
MODEL_PATH = 'saved_model.pb'
CSV_FILE = 'vm_data.csv'
DEFAULT_THRESHOLD_1 = 2000
DEFAULT_THRESHOLD_2 = 2000


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
    mem_total = mem_free = mem_buffers = mem_cached = 0
    for line in lines:
        if 'MemTotal' in line:
            mem_total = int(re.search(r'\d+', line).group())
        elif 'MemFree' in line:
            mem_free = int(re.search(r'\d+', line).group())
        elif 'Buffers' in line:
            mem_buffers = int(re.search(r'\d+', line).group())
        elif 'Cached' in line:
            mem_cached = int(re.search(r'\d+', line).group())

    mem_used = mem_total - (mem_free + mem_buffers + mem_cached)
    return mem_used


# Function to load TensorFlow model
def load_model():
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except Exception as e:
        print(f"Failed to load model: {e}")
        exit(1)


# Function to retrieve memory usage from VM1 (Apache server)
def get_memory_host_view(client):
    meminfo = client.get_data()
    return parse_memory_info(meminfo)


def get_vm2_data(client):
    data = client.get_data()
    response_time, bw_download, bw_upload = data.split(',')
    return float(response_time), int(bw_download), int(bw_upload)


def change_cgroup_limit(new_limit):
    cgroup_file_path = VM1_PATH_CGROUP_FILE
    try:
        with open(cgroup_file_path, "w") as f:
            f.write(str(new_limit))
    except FileNotFoundError as e:
        print(f"File not found - {e}")
        exit(1)
    except PermissionError as e:
        print(f"Permission Error - {e}")
        exit(1)


# Main function
def main():
    client_vm1 = Client(VM1_HOST, VM1_PORT)  # Apache server VM
    client_vm2 = Client(VM2_HOST, VM2_PORT)  # Client VM
    model = load_model()

    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Memory (VM view)', 'Memory (Host view)', 'CT', 'BW (Download)', 'BW (Upload)'])

        t = 0
        start_time = time.time()
        while t < DURATION:
            try:
                current_time = time.time()
                elapsed_time = current_time - start_time

                if elapsed_time >= FINESSE:
                    t += elapsed_time
                    start_time = current_time

                    mem_vm_view = parse_memory_info(client_vm1.get_data())
                    mem_host_view = get_memory_host_view(client_vm1)  # Use the client to get data from Apache server VM
                    response_time, bw_download, bw_upload = get_vm2_data(client_vm2)

                    writer.writerow([t, mem_vm_view, mem_host_view, response_time, bw_download, bw_upload])

                    # Model inference and cgroup adjustments
                    data_for_inference = np.array([[mem_vm_view, response_time, bw_download, bw_upload]])
                    predicted_value = model.predict(data_for_inference)

                    # Adjust cgroup based on predicted_value
                    if predicted_value < DEFAULT_THRESHOLD_1:
                        new_limit = int(mem_vm_view * (1 + FINESSE))
                        change_cgroup_limit(new_limit)
                    elif DEFAULT_THRESHOLD_1 < predicted_value < DEFAULT_THRESHOLD_2:
                        pass  # No change
                    else:
                        new_limit = int(mem_vm_view * (1 - FINESSE))
                        change_cgroup_limit(new_limit)
            except Exception as e:
                print(f"An error occurred: {e}")

        client_vm1.close()
        client_vm2.close()


if __name__ == "__main__":
    main()
