import matplotlib.pyplot as plt
import pandas as pd

CSV_FILE = 'outputs/vm_data_20240208-143939.csv'

# Load the dataset from CSV
data = pd.read_csv(CSV_FILE)

# Convert the 'Time' column to datetime for better plotting
data['Time'] = pd.to_datetime(data['Time'], unit='s')

# Plotting
plt.figure(figsize=(10, 5))

# Plot download bandwidth
plt.plot(data['Time'], data['BW (Download)'], label='Download Bandwidth', color='blue')

# Plot upload bandwidth
plt.plot(data['Time'], data['BW (Upload)'], label='Upload Bandwidth', color='red')

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
