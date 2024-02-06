import csv
import json
import time

import numpy as np

from lab.host.CGroupManager import CGroupManager
from lab.host.Log import log_runtime_action
from lab.host.client import Client
from lab.host.utils import parse_memory_info, load_model

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)
VM1_PATH_CGROUP_FILE = config["VM1_PATH_CGROUP_FILE"]
VM1_HOST = config["VM1_HOST"]
VM1_PORT = config["VM1_PORT"]
VM2_HOST = config["VM2_HOST"]
VM2_PORT = config["VM2_PORT"]
DURATION = config["DURATION"]
FINESSE = config["FINESSE"]
MODEL_PATH = config["MODEL_PATH"]
CSV_FILE = config["CSV_FILE"]
RUNTIME_ACTIONS_FILE = config["RUNTIME_ACTIONS_FILE"]
MIN_CGROUP_LIMIT = config["MIN_CGROUP_LIMIT"]
cgroup_manager = CGroupManager(config["VM1_PATH_CGROUP_FILE"], config["THRESHOLD_1"], config["THRESHOLD_2"])


def get_vm1_data(client_vm1):
    data = client_vm1.get_data()
    return parse_memory_info(data)


def get_vm2_data(client):
    data = client.get_data()
    response_time, bw_download, bw_upload = data.split(',')
    return float(response_time), int(bw_download), int(bw_upload)


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
                mem_vm_view = get_vm1_data(client_vm1)
                mem_host_view = cgroup_manager.get_cgroup_memory_limit()
                response_time, bw_download, bw_upload = get_vm2_data(client_vm2)

                # Model inference and cgroup adjustments
                data_for_inference = np.array([[mem_vm_view, response_time, bw_download, bw_upload]])
                predicted_value = model.predict(data_for_inference)
                action_taken = cgroup_manager.adjust_cgroup_limit(predicted_value, mem_vm_view)

                # Write data to the training log
                writer.writerow([t, mem_vm_view, mem_host_view, response_time, bw_download, bw_upload])

                # Log the runtime action
                log_runtime_action(t, cgroup_manager.get_cgroup_memory_limit(), action_taken)

        except Exception as e:
            print(f"An error occurred: {e}")

    client_vm1.close()
    client_vm2.close()


if __name__ == "__main__":
    main()
