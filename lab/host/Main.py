import argparse
import csv
import time

import numpy as np

from lab.common import Constants
from lab.common.Constants import FINESSE, VM1_IP, VM1_PORT, VM2_IP, VM2_PORT, DURATION, VM1_PATH_CGROUP_FILE, \
    HOST_PATH_CGROUP_FILE, THRESHOLD_1, THRESHOLD_2, BANDWIDTH_UPLOAD_VM_, BANDWIDTH_DOWNLOAD_VM_, RESPONSE_TIME_VM_, \
    SWAP_HOST_, MEMORY_HOST_, MEMORY_AVAILABLE_VM_, MEMORY_TOTAL_VM_, C_GROUP_LIMIT_VM_, TIME, MEMORY_USED_VM_
from lab.host.BandwidthMonitor import BandwidthMonitor
from lab.host.CGroupManager import CGroupManager
from lab.host.Client import Client
from lab.host.ScenarioManager import ScenarioManager
from lab.host.Utils import parse_memory_info, load_model, get_output_file_name

cgroup_manager = CGroupManager(VM1_PATH_CGROUP_FILE, HOST_PATH_CGROUP_FILE, THRESHOLD_1, THRESHOLD_2)
global continue_running


def get_vm1_data(apache):
    data = apache.get_data()
    return parse_memory_info(data)


def get_vm2_data(client):
    data = client.get_data()
    return float(data)


def generate_dataset(client_vm1, client_vm2, writer, bandwidth_monitor):
    mega = (1024 * 1024)
    current_cgroup_limit = cgroup_manager.get_cgroup_memory_limit_vm()
    print(f"    {C_GROUP_LIMIT_VM_}: {current_cgroup_limit / mega} MB")
    mem_total_vm, mem_available_view = get_vm1_data(client_vm1)
    print(f"    {MEMORY_TOTAL_VM_}: {mem_total_vm / mega} MB")
    print(f"    {MEMORY_AVAILABLE_VM_}: {mem_available_view / mega} MB")
    mem_used_vm = mem_total_vm - mem_available_view
    print(f"    {MEMORY_USED_VM_}: {mem_used_vm / mega} MB")
    mem_host_view = cgroup_manager.get_cgroup_memory_current_vm()
    print(f"    {MEMORY_HOST_}: {mem_host_view / mega} MB")
    mem_swap = cgroup_manager.get_swap_used_hostview()
    print(f"    {SWAP_HOST_}: {mem_swap / mega} MB")
    response_time = get_vm2_data(client_vm2)
    print(f"    {RESPONSE_TIME_VM_}: {response_time} ms")

    bw_download, bw_upload = bandwidth_monitor.get_bandwidth()
    print(f"    {BANDWIDTH_DOWNLOAD_VM_}: {bw_download / mega} MB")
    print(f"    {BANDWIDTH_UPLOAD_VM_}: {bw_upload / mega} MB")

    current_cgroup_limit = cgroup_manager.get_cgroup_memory_limit_vm()
    print(f"    {C_GROUP_LIMIT_VM_}: {current_cgroup_limit / mega} MB")

    mem_total_vm, mem_available_view = get_vm1_data(client_vm1)
    print(f"    {MEMORY_TOTAL_VM_}: {mem_total_vm / mega} MB")
    print(f"    {MEMORY_AVAILABLE_VM_}: {mem_available_view / mega} MB")

    mem_used_vm = mem_total_vm - mem_available_view
    print(f"    {MEMORY_USED_VM_}: {mem_used_vm / mega} MB")

    mem_host_view = cgroup_manager.get_cgroup_memory_current_vm()
    print(f"    {MEMORY_HOST_}: {mem_host_view / mega} MB")

    mem_swap = cgroup_manager.get_swap_used_hostview()
    print(f"    {SWAP_HOST_}: {mem_swap / mega} MB")

    writer.writerow(
        [time.time(), current_cgroup_limit, mem_total_vm, mem_available_view, mem_used_vm, mem_host_view, mem_swap,
         response_time, bw_download, bw_upload])
    print("     Data written to CSV.")


def run_model_and_adjust(client_vm1, client_vm2, model, writer, bandwidth_monitor):
    mem_vm_view = get_vm1_data(client_vm1)
    mem_host_view = cgroup_manager.get_cgroup_memory_limit_host()
    response_time = get_vm2_data(client_vm2)
    bw_download, bw_upload = bandwidth_monitor.get_bandwidth()
    # Run the model
    input_data = np.array([[mem_vm_view, mem_host_view, response_time, bw_download, bw_upload]])
    action = model.predict(input_data)
    # Adjust the cgroup limit
    action_taken = cgroup_manager.adjust_cgroup_limit_vm(action, mem_vm_view)
    # Write to CSV
    writer.writerow([time.time(), mem_vm_view, mem_host_view, response_time, bw_download, bw_upload, action_taken])


def scenario_callback(action, scenario_index):
    global continue_running
    if action == 'start':
        print(f"Starting scenario {scenario_index}")
    elif action == 'end':
        print(f"Ending scenario {scenario_index}")
    elif action == 'complete':
        print("All scenarios completed")
        continue_running = False


def main():
    global continue_running
    continue_running = True

    parser = argparse.ArgumentParser(description='Control operation mode of the script.')
    parser.add_argument('--mode', type=str, default='collect', choices=['collect', 'predict'],
                        help='Operation mode: "collect" to generate dataset, "predict" to run model and adjust cgroup.')
    args = parser.parse_args()
    # generate scenarios
    scenarios = [(1024, 60), (768, 60), (512, 60), (396, 60), (512, 60)
        , (768, 60), (1024, 60), (768, 60), (512, 60), (396, 60)]
    scenario_manager = ScenarioManager(cgroup_manager, scenarios, scenario_callback)
    scenario_manager.start()  # Start scenario management in a separate thread

    bandwidth_monitor = BandwidthMonitor(Constants.INTERFACE, Constants.VM1_IP, Constants.PCAP_FILE)

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
            header = [TIME, C_GROUP_LIMIT_VM_, MEMORY_TOTAL_VM_, MEMORY_AVAILABLE_VM_, MEMORY_USED_VM_, MEMORY_HOST_,
                      SWAP_HOST_, RESPONSE_TIME_VM_, BANDWIDTH_DOWNLOAD_VM_, BANDWIDTH_UPLOAD_VM_]
            if args.mode == 'predict':
                header.append('Action Taken')

            writer.writerow(header)

            t = 0
            start_time = time.time()
            while t < DURATION and continue_running:
                current_time = time.time()
                elapsed_time = current_time - start_time

                if elapsed_time >= FINESSE:
                    print(f"Elapsed time: {t} seconds")
                    t += elapsed_time
                    start_time = current_time

                    if args.mode == 'collect':
                        print("Generating dataset...")
                        generate_dataset(client_vm1, client_vm2, writer, bandwidth_monitor)
                    elif args.mode == 'predict':
                        print("Running model and adjusting cgroup...")
                        run_model_and_adjust(client_vm1, client_vm2, model, writer, bandwidth_monitor)

                    file.flush()
    finally:
        scenario_manager.stop()
        bandwidth_monitor.stop()
        client_vm1.close()
        client_vm2.close()
        print("Script terminated.")


if __name__ == "__main__":
    main()
