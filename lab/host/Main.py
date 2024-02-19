import argparse
import csv
import threading
import time

from lab.common import Constants
from lab.common.Constants import BANDWIDTH_DOWNLOAD_VM_, BANDWIDTH_UPLOAD_VM_, C_GROUP_LIMIT_VM_
from lab.host.BandwidthMonitor import BandwidthMonitor
from lab.host.CGroupManager import CGroupManager
from lab.host.Client import Client
from lab.host.ScenarioManager import ScenarioManager
from lab.host.Utils import parse_memory_info, load_model, get_output_file_name

continue_running = True
csv_file_lock = threading.Lock()


def get_vm1_data(apache):
    data = apache.get_data()
    return parse_memory_info(data)


def get_vm2_data(client):
    data = client.get_data()
    return float(data)


def generate_dataset(client_vm1, client_vm2, writer, bandwidth_monitor, cgroup_manager):
    while continue_running:
        mega = 1024 * 1024
        response_time = get_vm2_data(client_vm2)
        print(f"    {Constants.RESPONSE_TIME_VM_}: {response_time} ms")

        bw_download, bw_upload = bandwidth_monitor.get_bandwidth()
        print(f"    {BANDWIDTH_DOWNLOAD_VM_}: {bw_download / mega} MB")
        print(f"    {BANDWIDTH_UPLOAD_VM_}: {bw_upload / mega} MB")

        current_cgroup_limit = cgroup_manager.get_cgroup_memory_limit_vm()
        print(f"    {C_GROUP_LIMIT_VM_}: {current_cgroup_limit / mega} MB")

        mem_total_vm, mem_available_vm = get_vm1_data(client_vm1)
        print(f"    {Constants.MEMORY_TOTAL_VM_}: {mem_total_vm / mega} MB")
        print(f"    {Constants.MEMORY_AVAILABLE_VM_}: {mem_available_vm / mega} MB")
        mem_used_vm = mem_total_vm - mem_available_vm
        print(f"    {Constants.MEMORY_USED_VM_}: {mem_used_vm / mega} MB")

        mem_host_view = cgroup_manager.get_cgroup_memory_current_vm()
        print(f"    {Constants.MEMORY_HOST_}: {mem_host_view / mega} MB")

        mem_swap = cgroup_manager.get_swap_used_hostview()
        print(f"    {Constants.SWAP_HOST_}: {mem_swap / mega} MB")

        with csv_file_lock:
            writer.writerow(
                [time.time(), current_cgroup_limit, mem_total_vm, mem_available_vm, mem_used_vm, mem_host_view,
                 mem_swap, response_time, bw_download, bw_upload])
        time.sleep(Constants.FINESSE)


def scenario_callback(action, scenario_index):
    if action == 'start':
        print(f"Starting scenario {scenario_index}")
    elif action == 'end':
        print(f"Ending scenario {scenario_index}")
    elif action == 'complete':
        print("All scenarios completed")
        global continue_running
        continue_running = False


def main():
    parser = argparse.ArgumentParser(description='Control operation mode of the script.')
    parser.add_argument('--mode', type=str, default='collect', choices=['collect', 'predict'],
                        help='Operation mode: "collect" to generate dataset, "predict" to run model and adjust cgroup.')
    args = parser.parse_args()

    apache = Client(Constants.VM1_IP, Constants.VM1_PORT)
    client = Client(Constants.VM2_IP, Constants.VM2_PORT)
    bandwidth_monitor = BandwidthMonitor(Constants.INTERFACE, Constants.VM1_IP, Constants.PCAP_FILE)
    cgroup_manager = CGroupManager(Constants.VM1_PATH_CGROUP_FILE, Constants.HOST_PATH_CGROUP_FILE,
                                   Constants.THRESHOLD_1, Constants.THRESHOLD_2)
    scenario_manager = ScenarioManager(cgroup_manager, Constants.SCENARIOS, scenario_callback)

    csv_filename = get_output_file_name()
    print(f"Output file: {csv_filename}")

    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        header = [Constants.TIME, Constants.C_GROUP_LIMIT_VM_, Constants.MEMORY_TOTAL_VM_,
                  Constants.MEMORY_AVAILABLE_VM_, Constants.MEMORY_USED_VM_, Constants.MEMORY_HOST_,
                  Constants.SWAP_HOST_, Constants.RESPONSE_TIME_VM_, Constants.BANDWIDTH_DOWNLOAD_VM_,
                  Constants.BANDWIDTH_UPLOAD_VM_]
        if args.mode == 'predict':
            header.append(Constants.ACTION_TAKEN)
        writer.writerow(header)

        if args.mode == 'predict':
            model = load_model()
            print("Model loaded")
        elif args.mode == 'collect':
            model = None
            data_thread = threading.Thread(target=generate_dataset,
                                           args=(apache, client, writer, bandwidth_monitor, cgroup_manager))
            data_thread.start()
            scenario_manager.start()
            data_thread.join()

    scenario_manager.stop()
    print("Script completed.")


if __name__ == "__main__":
    main()
