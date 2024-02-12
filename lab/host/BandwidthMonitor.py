from threading import Thread, Lock

from scapy.all import sniff
from scapy.layers.inet import IP


class BandwidthMonitor:
    """
    Monitor bandwidth usage on a specific interface and IP address
    """

    def __init__(self, interface, vm_ip):
        self.interface = interface
        self.vm_ip = vm_ip
        self.bw_download = 0
        self.bw_upload = 0
        self.lock = Lock()
        self.thread = Thread(target=self.monitor_bandwidth, daemon=True)
        self.thread.start()

    def packet_callback(self, packet):
        try:
            if IP in packet:
                packet_length = len(packet)
                if packet[IP].src == self.vm_ip:
                    # Outgoing packet of the server
                    with self.lock:
                        self.bw_download += packet_length
                elif packet[IP].dst == self.vm_ip:
                    # Incoming packet of the server
                    with self.lock:
                        self.bw_upload += packet_length
        except Exception as e:
            print(f"Error processing packet: {e}")

    def monitor_bandwidth(self):
        try:
            sniff(iface=self.interface, prn=self.packet_callback, store=False)
        except Exception as e:
            print(f"Error monitoring bandwidth: {e}")

    def get_bandwidth(self):
        with self.lock:
            bw_download = self.bw_download
            bw_upload = self.bw_upload
            self.bw_download = 0
            self.bw_upload = 0
        return bw_download, bw_upload

    def stop(self):
        self.thread.join()
