import csv
import re
import time

import numpy as np
import tensorflow as tf

from lab.host.client import Client

# VM 1: Apache server VM
VM1_PATH_CGROUP_FILE = "/sys/fs/cgroup/machine.slice/machine-qemu\\x2d6\\x2dubuntu22.04.scope"
VM1_CGROUP_MEMORY_MAX = VM1_PATH_CGROUP_FILE + "/memory.max"
VM1_CGROUP_MEMORY_CURRENT = VM1_PATH_CGROUP_FILE + "/memory.current"
VM1_HOST = '192.168.100.175'  # IP of VM1
VM1_PORT = 8000

# VM 2: Client VM
VM2_HOST = '192.168.100.231'  # IP of VM2
VM2_PORT = 8000

# Constants
DURATION = 99999
FINESSE = 0.5
MODEL_PATH = '.'
CSV_FILE = 'vm_data.csv'
RUNTIME_ACTIONS_FILE = 'runtime_actions.csv'
DEFAULT_THRESHOLD_1 = 2000
DEFAULT_THRESHOLD_2 = 2000
MIN_CGROUP_LIMIT = 1000000  # 1GB


def parse_memory_info(meminfo):
    """
    Return the memory used by the VM in bytes.
    The input is the output of /proc/meminfo file in the VM (as a string).
    This value is calculated as the difference between the total memory and the sum of free, buffered and cached memory.
    """
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


def load_model():
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except Exception as e:
        print(f"Failed to load model: {e}")
        exit(1)


def get_vm2_data(client):
    data = client.get_data()
    response_time, bw_download, bw_upload = data.split(',')
    return float(response_time), int(bw_download), int(bw_upload)


def change_cgroup_limit(new_limit):
    try:
        with open(VM1_CGROUP_MEMORY_MAX, "w") as f:
            f.write(str(new_limit))
    except FileNotFoundError as e:
        print(f"File not found - {e}")
        exit(1)
    except PermissionError as e:
        print(f"Permission Error - {e}")
        exit(1)


def get_cgroup_memory_limit():
    try:
        with open(VM1_CGROUP_MEMORY_CURRENT, 'r') as file:
            current_usage = file.read().strip()
            return int(current_usage)
    except IOError as e:
        print(f"Error reading {VM1_CGROUP_MEMORY_CURRENT}: {e}")
        return None


def adjust_cgroup_limit(predicted_value, mem_vm_view):
    if predicted_value < DEFAULT_THRESHOLD_1:
        new_limit = max(int(mem_vm_view * (1 + FINESSE)), MIN_CGROUP_LIMIT)
        change_cgroup_limit(new_limit)
        return -1
    elif predicted_value >= DEFAULT_THRESHOLD_2:
        new_limit = max(int(mem_vm_view * (1 - FINESSE)), MIN_CGROUP_LIMIT)
        change_cgroup_limit(new_limit)
        return 1
    else:
        return 0


def log_runtime_action(time, mem_limit, action_taken):
    with open(RUNTIME_ACTIONS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time, mem_limit, action_taken])


def main():
    client_vm1 = Client(VM1_HOST, VM1_PORT)  # Apache server VM
    client_vm2 = Client(VM2_HOST, VM2_PORT)  # Client VM
    model = load_model()

    # Initialize the runtime actions log file
    with open(RUNTIME_ACTIONS_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time', 'Memory Limit', 'Action Taken'])

    # Initialize the training data log file
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

                # Fetch data from VMs
                mem_vm_view = parse_memory_info(client_vm1.get_data())
                mem_host_view = get_cgroup_memory_limit()
                response_time, bw_download, bw_upload = get_vm2_data(client_vm2)

                # Model inference and cgroup adjustments
                data_for_inference = np.array([[mem_vm_view, response_time, bw_download, bw_upload]])
                predicted_value = model.predict(data_for_inference)
                action_taken = adjust_cgroup_limit(predicted_value, mem_vm_view)

                # Write data to the training log
                writer.writerow([t, mem_vm_view, mem_host_view, response_time, bw_download, bw_upload])

                # Log the runtime action
                log_runtime_action(t, get_cgroup_memory_limit(), action_taken)

        except Exception as e:
            print(f"An error occurred: {e}")

    client_vm1.close()
    client_vm2.close()


def log_training(bw_download, bw_upload, mem_host_view, mem_vm_view, response_time, t, writer):
    writer.writerow([t, mem_vm_view, mem_host_view, response_time, bw_download, bw_upload])


if __name__ == "__main__":
    main()
