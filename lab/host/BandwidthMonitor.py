from threading import Thread, Lock

from scapy.all import sniff
from scapy.layers.inet import IP

from lab.common import Constants


class BandwidthMonitor:
    """
    Monitor bandwidth usage on a specific interface and IP address
    """

    def __init__(self, interface, vm_ip):
        self.should_stop = False
        self.interface = interface
        self.vm_ip = vm_ip
        self.bw_download = 0
        self.bw_upload = 0
        self.lock = Lock()
        self.thread = Thread(target=self.monitor_bandwidth, daemon=True)
        self.thread.start()

    def packet_callback(self, packet):
        if IP in packet and (packet[IP].src == self.vm_ip or packet[IP].dst == self.vm_ip):
            packet_length = len(packet)
            with self.lock:
                if packet[IP].src == self.vm_ip:
                    # Outgoing packet
                    self.bw_download += packet_length
                elif packet[IP].dst == self.vm_ip:
                    # Incoming packet
                    self.bw_upload += packet_length

    def monitor_bandwidth(self):
        while not self.should_stop:
            try:
                sniff(filter="ip", iface=self.interface, prn=self.packet_callback, store=False,
                      timeout=Constants.FINESSE)
            except Exception as e:
                print(f"Error monitoring bandwidth: {e}")

    def get_bandwidth(self):
        with self.lock:
            bw_download = self.bw_download
            bw_upload = self.bw_upload
            self.bw_download = 0
            self.bw_upload = 0
        print(f"Bandwidth: {bw_download} {bw_upload}")
        return bw_download, bw_upload

    def stop(self):
        self.should_stop = True
        self.thread.join()
