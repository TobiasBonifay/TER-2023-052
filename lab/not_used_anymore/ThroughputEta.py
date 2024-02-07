import pcapy
import time
from struct import *

dev = "virbr10"
max_bytes = 65536
promiscuous = False
read_timeout = 100

last_time = time.time()
total_bytes = 0
rates = []


def handle_packet(packet):
    global total_bytes, last_time

    total_bytes += len(packet)

    current_time = time.time()
    elapsed_time = current_time - last_time

    if elapsed_time > 1.0:
        rate = total_bytes / elapsed_time
        print(f"Rate: {rate / (1024 * 1024):.2f} MB/s")
        rates.append(rate)
        total_bytes = 0
        last_time = current_time


def main():
    pcap = pcapy.open_live(dev, max_bytes, promiscuous, read_timeout)
    pcap.loop(0, handle_packet)


if __name__ == "__main__":
    main()
