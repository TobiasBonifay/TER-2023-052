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

    def get_data(self):
        BUFFER_SIZE = 4096
        data = self.client.recv(BUFFER_SIZE).decode()

        # Processing data stream...
        response_times = []
        buffer = ''
        buffer += data
        while '\n' in buffer:
            response_time_str, buffer = buffer.split('\n', 1)
            response_times.append(response_time_str)

        return response_times

    def close(self):
        self.client.close()
