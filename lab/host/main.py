import csv
import socket
import time
import numpy as np
import tensorflow as tf

# Constants and configurations
VM1_PATH_CGROUP_FILE = "/sys/fs/cgroup/machine.slice/machine-qemu\\x2d6\\x2dubuntu22.04.scope/memory.max"
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
def main(self):
    client_vm1 = Client(VM1_HOST, VM1_PORT)
    client_vm2 = Client(VM2_HOST, VM2_PORT)
    model = load_model()

    with open('vm_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Memory (VM view)', 'Memory (Host view)', 'CT', 'BW (Download)', 'BW (Upload)'])

        while self.t < DURATION:
            mem_vm_view, mem_host_view = parse_memory_info(client_vm1.get_data())
            response_time, bw_download, bw_upload = get_vm2_data(client_vm2)

            writer.writerow([  # Write data to CSV
                self.t,  # Time
                self.memorygetter.get_mem_proc() / 1048576,  # Memory (VM view) in MB
                self.clientMemVm.get_used_memory() / 1024,  # Memory (Host view) in KB
                response_time,  # CT
                bw_download,  # BW (Download)
                bw_upload  # BW (Upload)
            ])
            # Model inference and cgroup adjustments
            data_for_inference = np.array([[mem_vm_view, response_time, bw_download, bw_upload]])
            predicted_value = model.predict(data_for_inference)
            # Adjust cgroup based on predicted_value


            time.sleep(FINESSE)

        client_vm1.close()
        client_vm2.close()


if __name__ == "__main__":
    main()
