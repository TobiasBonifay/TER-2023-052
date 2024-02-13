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

# Plotting
plt.figure(figsize=(12, 15))

# Plot download bandwidth
plt.plot(data['Time'], data['BW (Download)'] * 10, label='Download Bandwidth', color='blue')

# Plot upload bandwidth
plt.plot(data['Time'], data['BW (Upload)'] * 100, label='Upload Bandwidth', color='red')

# Plot memory usage
plt.plot(data['Time'], data['Memory (VM view)'] * 100, label='Memory Usage (VM view)', color='green')

# Plot memory limit
plt.plot(data['Time'], data['Memory (Host view)'], label='Memory Limit (Host view)', color='orange')

# Plot response time
plt.plot(data['Time'], data['CT'] * 1000 * 1000, label='Response Time', color='purple')

plt.grid(True)

# Add some labels and a legend
plt.xlabel('Time')
plt.ylabel('Bandwidth (bytes)')
plt.title('Bandwidth Usage Over Time')
plt.legend()

# Show the plot
plt.tight_layout()
plt.show()
