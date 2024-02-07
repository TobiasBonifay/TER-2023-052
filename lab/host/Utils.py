import re

import tensorflow as tf

from lab.Constants import MODEL_PATH


def parse_memory_info(meminfo):
    """
    Return the memory used by the VM in bytes.
    The input is the output of /proc/meminfo file in the VM (as a string).
    This value is calculated as the difference between the total memory and the sum of free, buffered and cached memory.
    """
    lines = meminfo.split('\n')
    mem_total = mem_free = mem_buffers = mem_cached = 0
    for line in lines:
        if 'MemTotal' in line:
            mem_total = int(re.search(r'\d+', line).group())
        elif 'MemFree' in line:
            mem_free = int(re.search(r'\d+', line).group())
        elif 'Buffers' in line:
            mem_buffers = int(re.search(r'\d+', line).group())
        elif 'Cached' in line:
            mem_cached = int(re.search(r'\d+', line).group())

    mem_used = mem_total - (mem_free + mem_buffers + mem_cached)
    return mem_used


def load_model():
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except Exception as e:
        print(f"Failed to load model: {e}")
        exit(1)
