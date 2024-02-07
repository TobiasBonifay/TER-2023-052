from lab.host.Main import FINESSE, MIN_CGROUP_LIMIT


class CGroupManager:
    def __init__(self, vm_path_cgroup_file, hypervisor_path_cgroup_file, threshold_1=2000, threshold_2=2000):
        self.vm_path_cgroup_file = vm_path_cgroup_file
        self.vm_cgroup_memory_max = vm_path_cgroup_file + "/memory.max"
        self.vm_cgroup_memory_current = vm_path_cgroup_file + "/memory.current"
        self.threshold_1 = threshold_1
        self.threshold_2 = threshold_2
        self.hypervisor_path_cgroup_file = hypervisor_path_cgroup_file

    def change_cgroup_limit_vm(self, new_limit):
        try:
            with open(self.vm_cgroup_memory_max, "w") as f:
                f.write(str(new_limit))
        except FileNotFoundError as e:
            print(f"File not found - {e}")
            exit(1)
        except PermissionError as e:
            print(f"Permission Error - {e}")
            exit(1)

    def get_cgroup_memory_limit_vm(self):
        try:
            with open(self.vm_cgroup_memory_current, 'r') as file:
                current_usage = file.read().strip()
                return int(current_usage)
        except IOError as e:
            print(f"Error reading {self.vm_cgroup_memory_current}: {e}")
            return None

    def adjust_cgroup_limit_vm(self, predicted_value, mem_vm_view):
        if predicted_value < self.threshold_1:
            new_limit = max(int(mem_vm_view * (1 + FINESSE)), MIN_CGROUP_LIMIT)
            self.change_cgroup_limit_vm(new_limit)
            return -1
        elif predicted_value >= self.threshold_2:
            new_limit = max(int(mem_vm_view * (1 - FINESSE)), MIN_CGROUP_LIMIT)
            self.change_cgroup_limit_vm(new_limit)
            return 1
        else:
            return 0

    def get_cgroup_memory_limit_host(self):
        try:
            with open(self.hypervisor_path_cgroup_file, 'r') as file:
                current_limit = file.read().strip()
                return int(current_limit)
        except IOError as e:
            print(f"Error reading {self.hypervisor_path_cgroup_file}: {e}")
            return None
