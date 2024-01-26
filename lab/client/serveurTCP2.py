import socket
import time

"""This TCP server is in the client (VM2) and is used to communicate with the host (this PC) the response time of the 
apache server every 45s"""

HOST = '0.0.0.0'
PORT = 8001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"Listening {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    print(f"Connected by {addr}")

    while True:
        response_time = "placeholder_response_time"
        conn.sendall(response_time.encode())
        time.sleep(45)

    conn.close()
    print(f"Disconnected from {addr}")
