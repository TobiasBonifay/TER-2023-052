import os

import matplotlib.pyplot as plt
import pandas as pd

from lab.common.Constants import BANDWIDTH_UPLOAD_VM_, BANDWIDTH_DOWNLOAD_VM_, RESPONSE_TIME_VM_, \
    SWAP_HOST_, MEMORY_HOST_, C_GROUP_LIMIT_VM_, MEMORY_USED_VM_


# Function to get the latest file in a directory
def latest_file(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)


CSV_PATH = '/home/tobias/TER-2023-052/lab/outputs/'
CSV_FILE = latest_file(CSV_PATH)
# CSV_FILE = '/home/tobias/TER-2023-052/lab/outputs/vm_data_20240214-113254.csv'

# Load the dataset from CSV
data = pd.read_csv(CSV_FILE)

# Convert the 'Time' column to datetime for better plotting
data['Time'] = pd.to_datetime(data['Time'], unit='s')

# Setting up the subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

# First plot for bandwidth
MEGA = 1024 * 1024
ax1.plot(data['Time'], data[BANDWIDTH_DOWNLOAD_VM_] / MEGA, '-o', label=BANDWIDTH_DOWNLOAD_VM_, color='blue')
ax1.plot(data['Time'], data[BANDWIDTH_UPLOAD_VM_] / MEGA, '-o', label=BANDWIDTH_UPLOAD_VM_, color='green')
ax1.set_xlabel('Time')
ax1.set_ylabel('Bandwidth (Mo/s)')
ax1.set_title('Bandwidth Usage Over Time')
ax1.legend()
ax1.grid(True)

# Second plot for memory usage
ax2.plot(data['Time'], data[C_GROUP_LIMIT_VM_] / MEGA, '-o', label=C_GROUP_LIMIT_VM_, color='red')
# ax2.plot(data['Time'], data[MEMORY_TOTAL_VM_] / MEGA, label=MEMORY_TOTAL_VM_, color='blue')
# ax2.plot(data['Time'], data[MEMORY_AVAILABLE_VM_] / MEGA, label=MEMORY_AVAILABLE_VM_, color='green')
ax2.plot(data['Time'], data[MEMORY_USED_VM_] / MEGA, '-o', label=MEMORY_USED_VM_, color='green')
ax2.plot(data['Time'], data[MEMORY_HOST_] / MEGA, '-o', label=MEMORY_HOST_, color='purple')
ax2.plot(data['Time'], data[SWAP_HOST_] / MEGA, '-o', label=SWAP_HOST_, color='orange')
ax2.set_xlabel('Time')
ax2.set_ylabel('Memory (Mo)')
ax2.set_title('Memory Usage Over Time')
ax2.legend()
ax2.grid(True)

# Third plot for response time
ax3.plot(data['Time'], data[RESPONSE_TIME_VM_], '-o', label=RESPONSE_TIME_VM_, color='blue')
ax3.set_xlabel('Time')
ax3.set_ylabel('Response Time (ms)')
ax3.set_title('Response Time Over Time')
ax3.legend()
ax3.grid(True)

# Show the plots
plt.show()
