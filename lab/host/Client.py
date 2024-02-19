import socket


class Client:
    """
    This class is used to get the information from the VMs.
    Do the connection to the VMs and get the data.
    """

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        self.client.settimeout(1)

    def get_data(self):
        try:
            data = self.client.recv(4096).decode()
            return data.strip()
        except socket.timeout:
            return None

    def close(self):
        self.client.close()
