from time import time, sleep

import pcapy

interface = "virbr10"
pcap = pcapy.open_live(interface, 65536, 1, 0)

start_time = time()
total_bytes = 0

while True:
    try:
        header, packet = pcap.next()
        total_bytes += len(packet)

        current_time = time()
        if current_time - start_time >= 1:
            throughput = total_bytes / (current_time - start_time)
            print(f"Throughput: {throughput} B/s")

            start_time = current_time
            total_bytes = 0

        sleep(0.1)
    except KeyboardInterrupt:
        break
