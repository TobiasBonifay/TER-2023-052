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
        Thread(target=self.monitor_bandwidth).start()

    def packet_callback(self, packet):
        if IP in packet:
            packet_length = len(packet)
            if packet[IP].src == self.vm_ip:
                # Outgoing packet
                with self.lock:
                    self.bw_upload += packet_length
            elif packet[IP].dst == self.vm_ip:
                # Incoming packet
                with self.lock:
                    self.bw_download += packet_length

    def monitor_bandwidth(self):
        sniff(iface=self.interface, prn=self.packet_callback, store=False)

    def get_bandwidth(self):
        with self.lock:
            bw_download = self.bw_download
            bw_upload = self.bw_upload
            self.bw_download = 0
            self.bw_upload = 0
        return bw_download, bw_upload
