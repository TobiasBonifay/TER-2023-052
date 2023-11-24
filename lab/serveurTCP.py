import re
import socket
import time

HOST = '0.0.0.0'
PORT = 8000


def get_memory_info():
    """
    Get memory info from /proc/meminfo file:

    mem_total: total memory in bytes
    mem_free: free memory in bytes
    buffers: memory used by buffers in bytes
    cached: memory used by cache in bytes

    mem_used = mem_total - mem_free - buffers - cached

    :return: string containing total memory used in bytes
    """
    with open("/proc/meminfo", "r") as file:
        meminfo = file.read()

    mem_total = mem_free = buffers = cached = 0
    for line in meminfo:
        if "MemTotal" in line:
            mem_total = int(re.findall(r'\d+', line)[0]) * 1024
        elif "MemFree" in line:
            mem_free = int(re.findall(r'\d+', line)[0]) * 1024
        elif "Buffers" in line:
            buffers = int(re.findall(r'\d+', line)[0]) * 1024
        elif "Cached" in line:
            cached = int(re.findall(r'\d+', line)[0]) * 1024

    mem_used = mem_total - mem_free - buffers - cached
    return str(mem_used)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Listening {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    print(f"Connected at {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break

        print(f"Received: {data.decode()}")
        mem_info = get_memory_info()
        print(f"Sending: {mem_info}")
        conn.sendall(mem_info.encode())

        time.sleep(1)

    conn.close()
    print(f"Disconnected from {addr}")
