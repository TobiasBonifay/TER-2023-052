import socket
import subprocess

from lab.config_loader import load_config

# Load configuration for the server
config = load_config()
HOST = config['VM1_HOST']  # The host address for the server
PORT = config['VM1_PORT']  # The port the server listens on


def get_memory_info():
    """Retrieve memory information from /proc/meminfo."""
    return subprocess.check_output(['cat', '/proc/meminfo']).decode()


def run_server(host, port):
    """Run the TCP server to send memory info to the client."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()

        print(f"Server listening on {host}:{port}")

        try:
            while True:
                conn, addr = server.accept()
                print(f"Connected by {addr}")

                try:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        response = get_memory_info()
                        conn.sendall(response.encode())
                finally:
                    conn.close()
                    print(f"Disconnected from {addr}")

        except KeyboardInterrupt:
            print("Server is shutting down.")


if __name__ == "__main__":
    run_server(HOST, PORT)
