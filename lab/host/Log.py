import csv

from lab.Constants import RUNTIME_ACTIONS_FILE


def log_runtime_action(time, mem_limit, action_taken):
    with open(RUNTIME_ACTIONS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time, mem_limit, action_taken])


def log_training(bw_download, bw_upload, mem_host_view, mem_vm_view, response_time, t, writer):
    writer.writerow([t, mem_vm_view, mem_host_view, response_time, bw_download, bw_upload])
