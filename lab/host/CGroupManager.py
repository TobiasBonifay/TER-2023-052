import os

from lab.common.Constants import MIN_CGROUP_LIMIT, FINESSE


class CGroupManager:
    def __init__(self, vm_path_cgroup_file, hypervisor_path_cgroup_file, threshold_1=2000, threshold_2=4000):
        self.vm_cgroup_memory_max = os.path.join(vm_path_cgroup_file, "memory.max")
        self.vm_cgroup_memory_current = os.path.join(vm_path_cgroup_file, "memory.current")
        self.hypervisor_path_cgroup_file = os.path.join(hypervisor_path_cgroup_file, "memory.current")
        self.hypervisor_path_cgroup_file_swap = os.path.join(hypervisor_path_cgroup_file, "memory.swap.current")
        self.threshold_1 = threshold_1
        self.threshold_2 = threshold_2

    # MAX MEMORY LIMIT FOR VM #
    def change_cgroup_limit_vm(self, new_limit):
        """
        Change the memory LIMIT for the VM.
        """
        try:
            with open(self.vm_cgroup_memory_max, "w") as f:
                print(f"Changing cgroup limit from {self.get_cgroup_memory_limit_vm()} to {new_limit}")
                f.write(str(new_limit))
        except FileNotFoundError as e:
            print(f"File not found - {e}")
            exit(1)
        except PermissionError as e:
            print(f"Permission Error - {e}")
            exit(1)

    def get_cgroup_memory_limit_vm(self):
        """
        Get the memory LIMIT for the VM. aka The max.
        """
        try:
            with open(self.vm_cgroup_memory_max, 'r') as file:
                current_limit = file.read().strip()
                if current_limit == "max":
                    print("Max limit found.")
                    return self.get_cgroup_memory_limit_host()
                return int(current_limit)
        except IOError as e:
            print(f"Error reading {self.vm_cgroup_memory_max}: {e}")
            return None

    # GET CURRENT MEMORY USAGE #
    def get_cgroup_memory_current_vm(self):
        """
        Get the CURRENT memory usage for the VM.
        """
        try:
            with open(self.vm_cgroup_memory_current, 'r') as file:
                current_usage = file.read().strip()
                return int(current_usage)
        except IOError as e:
            print(f"Error reading {self.vm_cgroup_memory_current}: {e}")
            return None

    def get_cgroup_memory_limit_host(self):
        """
        Get the CURRENT memory for the hypervisor.
        """
        try:
            with open(self.hypervisor_path_cgroup_file, 'r') as file:
                current_limit = file.read().strip()
                print(f"Current limit: {current_limit}")
                return int(current_limit)
        except IOError as e:
            print(f"Error reading {self.hypervisor_path_cgroup_file}: {e}")
            return None

    # ADJUST MEMORY LIMIT #
    def adjust_cgroup_limit_vm(self, predicted_value, mem_vm_view):
        """
        Adjust the memory limit of the VM based on the predicted value. aka Mechanism
        """
        if predicted_value < self.threshold_1:
            new_limit = max(int(mem_vm_view * (1 + FINESSE)), MIN_CGROUP_LIMIT)
            print(f"Predicted value: {predicted_value}, new limit: {new_limit}")
            self.change_cgroup_limit_vm(new_limit)
            return -1
        elif predicted_value >= self.threshold_2:
            new_limit = max(int(mem_vm_view * (1 - FINESSE)), MIN_CGROUP_LIMIT)
            print(f"Predicted value: {predicted_value}, new limit: {new_limit}")
            self.change_cgroup_limit_vm(new_limit)
            return 1
        else:
            return 0

    def get_swap_used_hostview(self):
        try:
            with open(self.hypervisor_path_cgroup_file_swap, 'r') as file:
                current_swap = file.read().strip()
                return int(current_swap)
        except IOError as e:
            print(f"Error reading {self.hypervisor_path_cgroup_file_swap}: {e}")
            return None
