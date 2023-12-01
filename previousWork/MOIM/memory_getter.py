import re


MOTIF = "\\d+"


class MemoryGetter:

    def __init__(self):
        self.VM_CGROUP_DIR = "/sys/fs/cgroup/machine.slice/machine-qemu\\x2d2\\x2ddebian12\\x2d1.scope/memory.max"
        self.VM_CGROUP_MAX_DIR = "/sys/fs/cgroup/machine.slice/machine-qemu\\x2d2\\x2ddebian12\\x2d1.scope/libvirt/memory.max"

    @staticmethod
    def get_mem_used():
        """
        Return the memory used by the VM in bytes
        """
        total_memory = free_memory = buffered_memory = cached_memory = 0
        with open("/proc/meminfo", "r") as f_meminfo:
            lines = f_meminfo.readlines()
            for line in lines:
                if "MemTotal" in line:
                    total_memory = int(re.findall(MOTIF, line)[0])
                if "MemFree" in line:
                    free_memory = int(re.findall(MOTIF, line)[0])
                if "Buffers" in line:
                    buffered_memory = int(re.findall(MOTIF, line)[0])
                if "Cached" in line:
                    cached_memory = int(re.findall(MOTIF, line)[0])

        used_memory = total_memory - free_memory - buffered_memory - cached_memory

        return used_memory

    @staticmethod
    def get_swap_used():
        """
        Return the swap used by the VM in bytes
        """
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
        """
        Return the memory used by the VM in bytes
        """
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
            exit(1)
        return limit_cgroup
