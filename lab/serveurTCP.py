import socket

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
        print(f"Received : {data.decode()}")
        conn.sendall(b"Response from server")
    conn.close()
