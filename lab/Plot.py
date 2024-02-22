import os

import matplotlib.pyplot as plt
import pandas as pd

from lab.common.Constants import BANDWIDTH_UPLOAD_VM_, BANDWIDTH_DOWNLOAD_VM_, RESPONSE_TIME_VM_, \
    SWAP_HOST_, MEMORY_HOST_, C_GROUP_LIMIT_VM_, ICMP_RESPONSE_TIME_VM_


# Function to get the latest file in a directory
def latest_file(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if basename.endswith('.csv')]
    return max(paths, key=os.path.getctime)


CSV_PATH = '/home/tobias/TER-2023-052/lab/outputs/'
CSV_FILE = latest_file(CSV_PATH)
# CSV_FILE = '/home/tobias/TER-2023-052/lab/outputs/vm_data_20240214-113254.csv'

# Load the dataset from CSV
data = pd.read_csv(CSV_FILE)

# Convert the 'Time' column to datetime for better plotting
data['Time'] = pd.to_datetime(data['Time'], unit='s')

# Setting up the subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12))
ax1_2 = ax1.twinx()
ax3_2 = ax3.twinx()
fig.patch.set_alpha(0.0)

# First plot for bandwidth
MEGA = 1024 * 1024
ax1_2.plot(data['Time'], data[BANDWIDTH_UPLOAD_VM_], '-o', label=BANDWIDTH_UPLOAD_VM_, color='red')
ax1.plot(data['Time'], data[BANDWIDTH_DOWNLOAD_VM_], '-o', label=BANDWIDTH_DOWNLOAD_VM_, color='blue')
ax1.set_ylabel('Bandwidth (Mo/s)')
ax1.set_title('Bandwidth Usage Over Time')
ax1.legend(loc='upper left')
ax1_2.legend(loc='upper right')
ax1.grid(True)

# Second plot for memory usage
ax2.plot(data['Time'], data[C_GROUP_LIMIT_VM_] / MEGA, '-o', label=C_GROUP_LIMIT_VM_, color='red')
# ax2.plot(data['Time'], data[MEMORY_TOTAL_VM_] / MEGA, label=MEMORY_TOTAL_VM_, color='blue')
# ax2.plot(data['Time'], data[MEMORY_AVAILABLE_VM_] / MEGA, label=MEMORY_AVAILABLE_VM_, color='green')
# ax2.plot(data['Time'], data[MEMORY_USED_VM_] / MEGA, '-o', label=MEMORY_USED_VM_, color='green')
ax2.plot(data['Time'], data[MEMORY_HOST_] / MEGA, '-o', label=MEMORY_HOST_, color='purple')
ax2.plot(data['Time'], data[SWAP_HOST_] / MEGA, '-o', label=SWAP_HOST_, color='orange')
ax2.set_ylabel('Memory (Mo)')
ax2.set_title('Memory Usage Over Time')
# tiny legend
ax2.legend(loc='upper left', bbox_to_anchor=(0, 1.05), ncol=2)
ax2.grid(True)

# Third plot for response time
# plot both
ax3.plot(data['Time'], data[RESPONSE_TIME_VM_], '-o', label=RESPONSE_TIME_VM_, color='red')
ax3.legend(loc='upper left')
ax3_2.plot(data['Time'], data[ICMP_RESPONSE_TIME_VM_], '-o', label=ICMP_RESPONSE_TIME_VM_, color='blue')
ax3_2.legend(loc='upper right')
ax3.set_ylabel('Response Time (ms)')
ax3_2.set_ylabel('ICMP Response Time (ms)')
ax3.set_title('Response Time Over Time')
ax3.grid(True)

# Show the plots
plt.show()
