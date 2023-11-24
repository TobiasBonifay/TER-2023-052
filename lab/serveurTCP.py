import socket
import time

HOST = '0.0.0.0'
PORT = 8000


def get_memory_info():
    """
    Get memory info from /proc/meminfo file
    :return: string containing memory info
    """
    with open("/proc/meminfo", "r") as file:
        meminfo = file.read()
    return meminfo


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
