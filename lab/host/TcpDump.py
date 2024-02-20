import subprocess
import threading


class TcpdumpThread(threading.Thread):
    """
    A class to run tcpdump in a separate thread.
    """
    def __init__(self, interface, vm_ip, output_file):
        super().__init__(daemon=True)
        self.interface = interface
        self.vm_ip = vm_ip
        self.output_file = output_file
        self.proc = None

    def run(self):
        print(f"Starting tcpdump on {self.interface} for {self.vm_ip}...")
        command = f"sudo tcpdump -i {self.interface} host {self.vm_ip} -s 60 -w {self.output_file}"
        self.proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def stop(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            print(f"tcpdump on {self.interface} for {self.vm_ip} stopped.")
