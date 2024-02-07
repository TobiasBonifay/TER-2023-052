import re
import socket

HOST = '192.168.100.231'
PORT = 8000
MOTIF = "\\d+"


class ClientMemVM:
    """
    Client TCP to get memory value from server (TcpMemProc.py)
    """

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client.connect((HOST, PORT))
        message = "I'm client"
        n = self.client.send(message.encode())
        if n != len(message):
            print('Sending error.')
        else:
            print("Connexion successful")

    def get_server(self):
        message = "GET"
        n = self.client.send(message.encode())
        if n != len(message):
            print('Sending error.')

    def get_values(self):
        self.get_server()
        data = self.client.recv(1024)
        return data.decode()

    def get_used_memory(self):
        data = self.get_values()
        lines = data.splitlines()
        total_memory = free_memory = buffered_memory = cached_memory = 0

        for line in lines:
            found = re.findall(MOTIF, line)
            if "MemTotal" in line and found:
                total_memory = int(found[0])
            if "MemFree" in line and found:
                free_memory = int(found[0])
            if "Buffers" in line and found:
                buffered_memory = int(found[0])
            if "Cached" in line and found:
                cached_memory = int(found[0])

        used_memory = total_memory - free_memory - buffered_memory - cached_memory
        return used_memory

    def close_client(self):
        self.client.close()
