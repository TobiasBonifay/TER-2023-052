import argparse
import csv
import time

import numpy as np

from lab.common.Constants import FINESSE, VM1_IP, VM1_PORT, VM2_IP, VM2_PORT, DURATION, VM1_PATH_CGROUP_FILE, \
    HOST_PATH_CGROUP_FILE, THRESHOLD_1, THRESHOLD_2
from lab.host.CGroupManager import CGroupManager
from lab.host.Client import Client
from lab.host.Utils import parse_memory_info, load_model, get_output_file_name

parser = argparse.ArgumentParser(description='Control operation mode of the script.')
parser.add_argument('--mode', type=str, default='collect', choices=['collect', 'predict'],
                    help='Operation mode: "collect" to generate dataset, "predict" to run model and adjust cgroup.')
args = parser.parse_args()

cgroup_manager = CGroupManager(VM1_PATH_CGROUP_FILE, HOST_PATH_CGROUP_FILE, THRESHOLD_1, THRESHOLD_2)


def get_vm1_data(client_vm1):
    data = client_vm1.get_data()
    return parse_memory_info(data)


def get_vm2_data(client):
    data = client.get_data()
    response_time, bw_download, bw_upload = data.split(',')
    return float(response_time), int(bw_download), int(bw_upload)


def generate_dataset(client_vm1, client_vm2, writer):
    mem_vm_view = get_vm1_data(client_vm1)
    mem_host_view = cgroup_manager.get_cgroup_memory_limit_host()
    response_time, bw_download, bw_upload = get_vm2_data(client_vm2)
    print(
        f"Memory (VM view): {mem_vm_view}, Memory (Host view): {mem_host_view}, CT: {response_time}, BW (Download): {bw_download}, BW (Upload): {bw_upload}")
    writer.writerow([time.time(), mem_vm_view, mem_host_view, response_time, bw_download, bw_upload])


def run_model_and_adjust(client_vm1, client_vm2, model, writer):
    mem_vm_view = get_vm1_data(client_vm1)
    mem_host_view = cgroup_manager.get_cgroup_memory_limit_host()
    response_time, bw_download, bw_upload = get_vm2_data(client_vm2)
    # Run the model
    input_data = np.array([[mem_vm_view, mem_host_view, response_time, bw_download, bw_upload]])
    action = model.predict(input_data)
    # Adjust the cgroup limit
    action_taken = cgroup_manager.adjust_cgroup_limit_vm(action, mem_vm_view)
    print(f"Memory (VM view): {mem_vm_view}, Memory (Host view): {mem_host_view}, CT: {response_time}"
          f", BW (Download): {bw_download}, BW (Upload): {bw_upload}, Action Taken: {action_taken}")
    # Write to CSV
    writer.writerow([time.time(), mem_vm_view, mem_host_view, response_time, bw_download, bw_upload, action_taken])


def main():
    model = None
    if args.mode == 'predict':
        model = load_model()

    client_vm1 = Client(VM1_IP, VM1_PORT)
    client_vm2 = Client(VM2_IP, VM2_PORT)

    csv_filename = get_output_file_name()
    print(f"Output file: {csv_filename}")

    try:
        # Initialize the CSV file writer and begin the main loop for data collection or prediction
        with open(csv_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            header = ['Time', 'Memory (VM view)', 'Memory (Host view)', 'CT', 'BW (Download)', 'BW (Upload)']
            if args.mode == 'predict':
                header.append('Action Taken')
            writer.writerow(header)

            t = 0
            start_time = time.time()
            while t < DURATION:
                current_time = time.time()
                elapsed_time = current_time - start_time

                if elapsed_time >= FINESSE:
                    t += elapsed_time
                    start_time = current_time
                    record_time = current_time  # Capture the timestamp for consistency

                    if args.mode == 'collect':
                        generate_dataset(client_vm1, client_vm2, writer)
                    elif args.mode == 'predict':
                        run_model_and_adjust(client_vm1, client_vm2, model, writer)

                    file.flush()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_vm1.close()
        client_vm2.close()


if __name__ == "__main__":
    main()
