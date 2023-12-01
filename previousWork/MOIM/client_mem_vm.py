import re
import socket

HOST = '192.168.100.175'
PORT = 8000
MOTIF = "\\d+"


class ClientMemVM:
    """
    Client TCP to get memory value from server (serveurTCP.py)
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
        # print(lines)
        for line in lines:
            if "MemTotal" in line:
                total_memory = int(re.findall(MOTIF, line)[0])
            if "MemFree" in line:
                free_memory = int(re.findall(MOTIF, line)[0])
            if "Buffers" in line:
                buffered_memory = int(re.findall(MOTIF, line)[0])
            if "Cached" in line:
                cached_memory = int(re.findall(MOTIF, line)[0])
        used_memory = total_memory - free_memory - buffered_memory - cached_memory
        print("CLIENT MEM VM Total memory: " + str(total_memory) + " kB")
        return used_memory

    def close_client(self):
        self.client.close()
