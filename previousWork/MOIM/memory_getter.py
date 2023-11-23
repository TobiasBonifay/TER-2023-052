import re

machine1 = "\\x2d1\\x2ddebian12\\x2d1.scope/"
machine2 = "\\x2d2\\x2ddebian12\\x2d2.scope/"

S = "/sys/fs/cgroup/machine.slice/machine-qemu"
MOTIF = "\d+"


class MemoryGetter:

    def __init__(self):
        self.VM_CGROUP_DIR = "%s%smemory.max" % (S, machine1)
        self.VM_CGROUP_DIR = "%s%smemory.max" % (S, machine1)
        self.VM_CGROUP_MAX_DIR = "%s%slibvirt/memory.max" % (S, machine1)
        self.MEM_VM_DIR = "~/Documents/surbooking-experiments/sockets"

    def get_mem_used(self):
        memtot = memfree = buff = cached = 0
        with open("/proc/meminfo", "r") as f_meminfo:
            lines = f_meminfo.readlines()
            for l in lines:
                if "MemTotal" in l:
                    memtot = int(re.findall(MOTIF, l)[0])
                if "MemFree" in l:
                    memfree = int(re.findall(MOTIF, l)[0])
                if "Buffers" in l:
                    buff = int(re.findall(MOTIF, l)[0])
                if "Cached" in l:
                    cached = int(re.findall(MOTIF, l)[0])

        memused = memtot - memfree - buff - cached

        return memused

    def get_swap_used(self):
        swaptot = swapfree = 0
        with open("/proc/meminfo", "r") as f_meminfo:
            lines = f_meminfo.readlines()
            for l in lines:
                if "SwapTotal" in l:
                    swaptot = int(re.findall(MOTIF, l)[0])
                if "SwapFree" in l:
                    swapfree = int(re.findall(MOTIF, l)[0])

        swap_used = swaptot - swapfree
        return swap_used

    def get_mem_proc(self):
        mem_proc = 0
        try:
            with open(self.VM_CGROUP_DIR, 'r') as f_memcurrent:
                mem_value = f_memcurrent.read().strip()
                if mem_value == 'max':
                    mem_proc = float('inf')
                else:
                    mem_proc = int(mem_value)
        except IOError as e:
            print(f"Error reading {self.VM_CGROUP_DIR}: {e}")
        except ValueError as e:
            print(f"Invalid value in {self.VM_CGROUP_DIR}: {e}")
        return mem_proc

    def get_limit_cgroup(self):
        limit_cgroup = 0
        try:
            with open(self.VM_CGROUP_MAX_DIR, 'r') as f_mem_max:
                limit = f_mem_max.read().strip()
                if limit == 'max':
                    limit_cgroup = float('inf')
                else:
                    limit_cgroup = int(limit)
        except IOError as e:
            print(f"Error reading {self.VM_CGROUP_MAX_DIR}: {e}")
        return limit_cgroup
