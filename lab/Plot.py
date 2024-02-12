import matplotlib.pyplot as plt
import pandas as pd

CSV_FILE = '/home/tobias/TER-2023-052/lab/outputs/vm_data_20240212-111916.csv'

# Load the dataset from CSV
data = pd.read_csv(CSV_FILE)

# Convert the 'Time' column to datetime for better plotting
data['Time'] = pd.to_datetime(data['Time'], unit='s')

# Plotting
plt.figure(figsize=(10, 8))

# Plot download bandwidth
# plt.plot(data['Time'], data['BW (Download)'], label='Download Bandwidth', color='blue')

# Plot upload bandwidth
plt.plot(data['Time'], data['BW (Upload)'], label='Upload Bandwidth', color='red')

# Plot memory usage
plt.plot(data['Time'], data['Memory (VM view)'], label='Memory Usage (VM view)', color='green')

# Plot memory limit
# plt.plot(data['Time'], data['Memory (Host view)'], label='Memory Limit (Host view)', color='orange')

# Plot response time
plt.plot(data['Time'], data['CT'], label='Response Time', color='purple')

plt.grid(True)

# Add some labels and a legend
plt.xlabel('Time')
plt.ylabel('Bandwidth (bytes)')
plt.title('Bandwidth Usage Over Time')
plt.legend()

# Rotate date labels
plt.xticks(rotation=45)

# Show the plot
plt.tight_layout()
plt.show()
