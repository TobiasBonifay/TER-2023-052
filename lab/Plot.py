import os

import matplotlib.pyplot as plt
import pandas as pd


# Function to get the latest file in a directory
def latest_file(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)


CSV_PATH = '/home/tobias/TER-2023-052/lab/outputs/'
CSV_FILE = latest_file(CSV_PATH)

# Load the dataset from CSV
data = pd.read_csv(CSV_FILE)

# Convert the 'Time' column to datetime for better plotting
data['Time'] = pd.to_datetime(data['Time'], unit='s')

# Setting up the subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 15))

# First plot for bandwidth
ax1.plot(data['Time'], data['BW (Download)'], label='Download Bandwidth', color='blue')
ax1.plot(data['Time'], data['BW (Upload)'], label='Upload Bandwidth', color='red')
ax1.set_xlabel('Time')
ax1.set_ylabel('Bandwidth (bytes)')
ax1.set_title('Bandwidth Usage Over Time')
ax1.legend()
ax1.grid(True)

# Second plot for memory usage
ax2.plot(data['Time'], data['Memory (VM view)'], label='Memory Usage (VM view)', color='green')
ax2.plot(data['Time'], data['Memory (Host view)'] / 1000, label='Memory Limit (Host view)', color='orange')
ax2.set_xlabel('Time')
ax2.set_ylabel('Memory (bytes)')
ax2.set_title('Memory Usage Over Time')
ax2.legend()
ax2.grid(True)

# Show the plots
plt.tight_layout()
plt.show()
