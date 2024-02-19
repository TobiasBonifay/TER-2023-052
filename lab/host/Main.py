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
from lab.host.TcpDump import TcpdumpThread
from lab.host.Utils import parse_memory_info, load_model, get_output_file_name

continue_running = True
csv_file_lock = threading.Lock()


def generate_dataset(client_vm1, client_vm2, writer, bandwidth_monitor, cgroup_manager):
    global continue_running, csv_file_lock
    mega = 1024 * 1024
    response_times = []
    bandwidth_tuples = []
    last_time = time.time()

    while continue_running:
        current_time = time.time()

        # If the finesse period has passed, calculate the average
        if current_time - last_time >= Constants.FINESSE:
            # Response time
            if response_times:
                response_time_average = sum(response_times) / len(response_times)
                response_times.clear()  # Reset for the next finesse period
            else:
                response_time_average = 0
            print(f"    {Constants.RESPONSE_TIME_VM_}: {response_time_average} ms")

            # Bandwidth
            if bandwidth_tuples:
                bw_download = sum([t[0] for t in bandwidth_tuples]) / len(bandwidth_tuples)
                bw_upload = sum([t[1] for t in bandwidth_tuples]) / len(bandwidth_tuples)
                bandwidth_tuples.clear()
            else:
                bw_download = 0
                bw_upload = 0
            print(f"    {BANDWIDTH_DOWNLOAD_VM_}: {bw_download / mega} MB")
            print(f"    {BANDWIDTH_UPLOAD_VM_}: {bw_upload / mega} MB")

            # VM memory
            current_cgroup_limit = cgroup_manager.get_cgroup_memory_limit_vm()
            print(f"    {C_GROUP_LIMIT_VM_}: {current_cgroup_limit / mega} MB")

            mem_total_vm, mem_available_vm = parse_memory_info(client_vm1.get_data())
            print(f"    {Constants.MEMORY_TOTAL_VM_}: {mem_total_vm / mega} MB")
            print(f"    {Constants.MEMORY_AVAILABLE_VM_}: {mem_available_vm / mega} MB")
            mem_used_vm = mem_total_vm - mem_available_vm
            print(f"    {Constants.MEMORY_USED_VM_}: {mem_used_vm / mega} MB")

            mem_host_view = cgroup_manager.get_cgroup_memory_current_vm()
            print(f"    {Constants.MEMORY_HOST_}: {mem_host_view / mega} MB")

            mem_swap = cgroup_manager.get_swap_used_hostview()
            print(f"    {Constants.SWAP_HOST_}: {mem_swap / mega} MB")

            last_time = current_time  # Reset the timer for the next finesse period
        else:
            # Collect the response time data
            response_time = client_vm2.get_data()
            if response_time is not None:
                try:
                    # Convert response time to float and append to the list
                    response_times.append(float(response_time))
                except ValueError:
                    # Handle the case where conversion to float fails
                    print(f"Invalid response time received: {response_time}")

            # Collect the bandwidth data
            bandwidth = bandwidth_monitor.get_bandwidth()
            if bandwidth is not None:
                bandwidth_tuples.append(bandwidth)

        # Sleep for a short interval to prevent tight looping
        time.sleep(0.1)  # A short sleep to prevent a tight loop that hogs the CPU


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

    csv_filename = get_output_file_name()
    pcap_filename = get_output_file_name("scapy_", Constants.PCAP_FILE)
    print(f"Output file: {csv_filename} and {pcap_filename}")

    bandwidth_monitor = BandwidthMonitor(Constants.INTERFACE, Constants.VM1_IP, pcap_filename)
    tcpdump_thread = TcpdumpThread(Constants.INTERFACE, Constants.VM1_IP, pcap_filename)
    cgroup_manager = CGroupManager(Constants.VM1_PATH_CGROUP_FILE, Constants.HOST_PATH_CGROUP_FILE,
                                   Constants.THRESHOLD_1, Constants.THRESHOLD_2)
    scenario_manager = ScenarioManager(cgroup_manager, Constants.SCENARIOS, scenario_callback)

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
            tcpdump_thread.start()
            data_thread.start()
            scenario_manager.start()
            data_thread.join()

    scenario_manager.stop()
    tcpdump_thread.stop()
    print("Script completed.")


if __name__ == "__main__":
    main()
