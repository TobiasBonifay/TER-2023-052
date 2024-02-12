import argparse
import csv
import time

import numpy as np

from lab.common import Constants
from lab.common.Constants import FINESSE, VM1_IP, VM1_PORT, VM2_IP, VM2_PORT, DURATION, VM1_PATH_CGROUP_FILE, \
    HOST_PATH_CGROUP_FILE, THRESHOLD_1, THRESHOLD_2
from lab.host.BandwidthMonitor import BandwidthMonitor
from lab.host.CGroupManager import CGroupManager
from lab.host.Client import Client
from lab.host.ScenarioManager import ScenarioManager
from lab.host.Utils import parse_memory_info, load_model, get_output_file_name

cgroup_manager = CGroupManager(VM1_PATH_CGROUP_FILE, HOST_PATH_CGROUP_FILE, THRESHOLD_1, THRESHOLD_2)


def get_vm1_data(apache):
    data = apache.get_data()
    return parse_memory_info(data)


def get_vm2_data(client):
    data = client.get_data()
    return float(data)


def generate_dataset(client_vm1, client_vm2, writer, bandwidth_monitor):
    mem_vm_view = get_vm1_data(client_vm1)
    print(f"    1 Memory (VM view): {mem_vm_view / (1024 * 1024)} GB")
    mem_host_view = cgroup_manager.get_cgroup_memory_limit_host()
    print(f"    2 Memory (Host view): {mem_host_view / (1024 * 1024 * 1024)} GB")
    response_time = get_vm2_data(client_vm2)
    print(f"    3 CT: {response_time} ms")
    bw_download, bw_upload = bandwidth_monitor.get_bandwidth()
    print(f"    4 BW (Download): {bw_download / (1024 * 1024)} MB/s, BW (Upload): {bw_upload / (1024 * 1024)} MB/s")
    # print(f"Memory (VM view): {mem_vm_view}, Memory (Host view): {mem_host_view}"
    #      f", CT: {response_time}, BW (Download): {bw_download}, BW (Upload): {bw_upload}")
    writer.writerow([time.time(), mem_vm_view, mem_host_view, response_time, bw_download, bw_upload])
    print("Data written to CSV.")


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
    print(f"Memory (VM view): {mem_vm_view}, Memory (Host view): {mem_host_view}, CT: {response_time}"
          f", BW (Download): {bw_download}, BW (Upload): {bw_upload}, Action Taken: {action_taken}")
    # Write to CSV
    writer.writerow([time.time(), mem_vm_view, mem_host_view, response_time, bw_download, bw_upload, action_taken])


def scenario_callback(action, scenario_index, num_scenarios):
    if action == 'start':
        print(f"Starting scenario {scenario_index}")
    elif action == 'end':
        print(f"Ending scenario {scenario_index}")
    if scenario_index == num_scenarios:
        print("All scenarios completed.")
        return True


def main():
    parser = argparse.ArgumentParser(description='Control operation mode of the script.')
    parser.add_argument('--mode', type=str, default='collect', choices=['collect', 'predict'],
                        help='Operation mode: "collect" to generate dataset, "predict" to run model and adjust cgroup.')
    args = parser.parse_args()

    scenarios = [(1500000000, 360),  # 1.5GB limit for 360 seconds
                 (1200000000, 360),  # 1.2GB limit for 360 seconds
                 (1000000000, 360),  # 1GB limit for 360 seconds
                 (900000000, 360),  # 900MB limit for 360 seconds
                 (800000000, 360),  # 800MB limit for 360 seconds
                 (700000000, 360),  # 700MB limit for 360 seconds
                 (600000000, 360),  # 600MB limit for 360 seconds
                 (500000000, 360),  # 500MB limit for 360 seconds
                 (400000000, 360),  # 400MB limit for 360 seconds
                 (300000000, 360),  # 300MB limit for 360 seconds
                 (200000000, 360)]  # 200MB limit for 360 seconds

    scenario_manager = ScenarioManager(cgroup_manager, scenarios, scenario_callback)
    scenario_manager.start()  # Start scenario management in a separate thread

    bandwidth_monitor = BandwidthMonitor(Constants.INTERFACE, Constants.VM1_IP)

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
                    print(f"Record time: {record_time}")

                    if args.mode == 'collect':
                        print("Generating dataset...")
                        generate_dataset(client_vm1, client_vm2, writer, bandwidth_monitor)
                    elif args.mode == 'predict':
                        print("Running model and adjusting cgroup...")
                        run_model_and_adjust(client_vm1, client_vm2, model, writer, bandwidth_monitor)

                    file.flush()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        bandwidth_monitor.stop()
        client_vm1.close()
        client_vm2.close()


if __name__ == "__main__":
    main()
