from threading import Thread, Lock

from scapy.all import sniff, wrpcap
from scapy.layers.inet import IP


class BandwidthMonitor:
    """
    Monitor bandwidth usage on a specific interface and IP address
    """

    def __init__(self, interface, vm_ip, pcap_file):
        self.should_stop = False
        self.interface = interface
        self.vm_ip = vm_ip
        self.bw_download = 0
        self.bw_upload = 0
        self.lock = Lock()
        self.pcap_file = pcap_file
        self.packets = []
        self.thread = Thread(target=self.monitor_bandwidth, daemon=True)
        self.thread.start()

    def packet_callback(self, packet):
        if IP in packet:
            packet_length = len(packet)
            with self.lock:
                self.packets.append(packet)
                if packet[IP].src == self.vm_ip:
                    # Outgoing packet
                    self.bw_download += packet_length
                elif packet[IP].dst == self.vm_ip:
                    # Incoming packet
                    self.bw_upload += packet_length

    def monitor_bandwidth(self):
        while not self.should_stop:
            try:
                sniff(iface=self.interface, prn=self.packet_callback, store=False, timeout=10)
                # Write packets to pcap file every 10 seconds
                with self.lock:
                    wrpcap(self.pcap_file, self.packets, append=True)
                    self.packets.clear()
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
        self.should_stop = True
        self.thread.join()
