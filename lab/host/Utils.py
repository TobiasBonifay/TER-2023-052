import os
import re
from datetime import datetime

import tensorflow as tf

from lab.common.Constants import MODEL_PATH


def get_output_file_name():
    # Get the current file's directory
    current_dir = os.path.dirname(__file__)

    # Go up one level to the 'lab' directory from 'lab/host'
    lab_dir = os.path.abspath(os.path.join(current_dir, '..'))

    # Ensure the 'outputs' directory exists inside the 'lab' directory
    outputs_dir = os.path.join(lab_dir, 'outputs')
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)

    # Generate the filename with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    csv_filename = f"vm_data_{timestamp}.csv"
    csv_filepath = os.path.join(outputs_dir, csv_filename)
    return csv_filepath


def parse_memory_info(meminfo):
    """
    Return the memory used by the VM in bytes.
    The input is the output of /proc/meminfo file in the VM (as a string).
    This value is calculated as the difference between the total memory and the sum of free, buffered and cached memory.
    """
    lines = meminfo.split('\n')
    mem_total = mem_free = mem_buffers = mem_cached = mem_available = 0
    for line in lines:
        if 'MemTotal' in line:
            mem_total = int(re.search(r'\d+', line).group())
            print(f"    MemTotal (MB): {mem_total / 1024}")
        elif 'MemFree' in line:
            mem_free = int(re.search(r'\d+', line).group())
            # print(f"    MemFree (MB): {mem_free / 1024}")
        elif 'Buffers' in line:
            mem_buffers = int(re.search(r'\d+', line).group())
            # print(f"    Buffers (MB): {mem_buffers / 1024}")
        elif 'Cached' in line and 'SwapCached' not in line:
            mem_cached = int(re.search(r'\d+', line).group())
            # print(f"    Cached (MB): {mem_cached / 1024}")
        elif 'MemAvailable' in line:
            mem_available = int(re.search(r'\d+', line).group())
            print(f"    MemAvailable (MB): {mem_available / 1024}")

    return mem_total * 1024, mem_available * 1024


def load_model():
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except Exception as e:
        print(f"Failed to load model: {e}")
        exit(1)
