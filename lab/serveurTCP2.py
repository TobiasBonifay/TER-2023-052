import socket
import time

"""
This TCP server is in the client (VM2) and is used to communicate with the host (this PC) the response time of the apache server every 45s
"""

HOST = '0.0.0.0'
PORT = 8000

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
        mem_info = "ok"  # send response time here
        print(f"Sending: {mem_info}")
        conn.sendall(mem_info.encode())

        time.sleep(45)

    conn.close()
    print(f"Disconnected from {addr}")
