import os
import time
import numpy as np
from threading import Thread

from keras.src.layers import RNN

from log import Log
from memory_getter import MemoryGetter
from client_mem_vm import ClientMemVM
from apache_benchmark import Benchmark
from inference import Inference
from colorama import init, Fore, Back, Style

DURATION = 99999
FINESSE = 0.5
TIME_RESPONSE = 0
THRESHOLD = 500

DEFAULT_THRESHOLD_1 = 2000
DEFAULT_THRESHOLD_2 = 2000

b = Benchmark()
log_ = Log()


def run_bench():
    global time_response
    time_response = 0
    while True:
        time_response = b.start_benchmark()


def change_limit_cgroup_file(cgroup_limit):
    cgroup_file_path = "/sys/fs/cgroup/machine.slice/machine-qemu\\x2d1\\x2ddebian12\\x2d1.scope/libvirt/memory.max"

    try:
        with open(cgroup_file_path, "w") as fmax:
            fmax.write(cgroup_limit)
    except FileNotFoundError as e:
        print(f"File not found - {e}")
        exit(1)
    except PermissionError as e:
        print(f"Run the script with administrator privileges - {e}")


def write_output(time, mem_limit, response_time, action):
    with open("out", "a") as f_out:
        f_out.write("{},{},{},{}\n".format(time, mem_limit, response_time, action))


class Mechanism:
    bash_tmp = []
    bash = []
    curr_tr_value = 0
    tr_list = np.zeros((0))
    t = 0
    first_threshold_coefficient = 1.3
    second_threshold_coefficient = 1.7

    def __init__(self, memorygetter, clientMemVm):
        self.memorygetter = memorygetter
        self.clientMemVm = clientMemVm
        self.infer = Inference()

    def run(self):

        start_time = time.process_time()
        write_output("time", "mem_limit", "time_response", "action")

        self.t = round(time.process_time() - start_time, 2)
        Thread(target=run_bench).start()
        while self.t < DURATION:
            diff_t = round(time.process_time() - self.t - start_time, 2)
            print("DEBUG " + str(diff_t) + " >= " + str(FINESSE) + " and " + str(time_response) + " > 0")
            if diff_t >= FINESSE and time_response > 0:  # we wait for the first value of the benchmark to perform an inference
                print("OK")
                self.t += diff_t
                self.update_bash()
                self.do_inference()
                print(Style.BRIGHT + Fore.GREEN + "[t = {} s]".format(int(self.t)), end="\r")

    def add_tr_to_list_tr(self, tr):
        """
        Add a new tr value to the list of tr values
        :param tr: time response value
        :return: None - update the list of tr values
        """
        if self.tr_list.shape[0] < 10 and tr != 0:
            self.tr_list = np.append(self.tr_list, tr)
        elif tr != 0:
            self.tr_list = np.roll(self.tr_list, -1)
            self.tr_list[-1] = tr

    def get_threshold(self):
        """
        Compute the threshold for the prediction of the next tr value

        if the tr value is NaN, we return the default value
        :return: threshold_1, threshold_2
        """
        if self.tr_list.size > 0:
            threshold_1, threshold_2 = np.mean(self.tr_list) * self.first_threshold_coefficient, np.mean(
                self.tr_list) * self.second_threshold_coefficient
        else:
            threshold_1, threshold_2 = DEFAULT_THRESHOLD_1, DEFAULT_THRESHOLD_2
        log_.debug("Threshold 1 = {} - Threshold 2 = {}".format(threshold_1, threshold_2))
        log_.debug(self.tr_list)
        return threshold_1, threshold_2

    def update_bash(self):
        if np.array(self.bash_tmp).shape[0] < 25:
            self.bash_tmp.append([
                self.memorygetter.get_mem_proc() / 1048576,  # in MB
                self.clientMemVm.get_used_memory() / 1024,  # in kB
                self.memorygetter.get_limit_cgroup() / 1048576,  # in MB
                time_response  # in ms
            ])
        else:
            self.bash = self.bash_tmp
            self.bash_tmp = []

    def do_inference(self):
        """
        We do prediction only when we have a new time response value that prevent us to cut lower the cgroup limit
        too frequently and make a prediction with tr value that are not descriptive of the VM state
        :return: None - update the cgroup limit
        """
        if self.curr_tr_value != time_response and np.array(self.bash).shape[0] == 25:
            self.add_tr_to_list_tr(self.curr_tr_value)
            self.do_predict()
            self.curr_tr_value = time_response

    def do_predict(self):
        """
        Do the prediction of the next tr value
        :return: None - update the cgroup limit
        """
        x_bash = np.array([self.bash])
        x_bash[0, :, -1] = time_response
        tr_predict = self.infer.predict(x_bash)
        log_.output("(tr predict is - " + str(tr_predict[0]) + ") (tr current is - " + str(self.curr_tr_value) + ")")
        self.change_limit_cgroup(tr_predict[0])

    def change_limit_cgroup(self, tr_predict):

        threshold_1, threshold_2 = self.get_threshold()

        limit_cgroup = self.memorygetter.get_limit_cgroup()
        # if the limit cgroup is not set, we set it to the double of the current memory used
        if self.memorygetter.get_limit_cgroup() == float('inf'):
            limit_cgroup = self.memorygetter.get_mem_used() * 2
            change_limit_cgroup_file(str(limit_cgroup))
            log_.debug("limit_cgroup - " + str(int(limit_cgroup / 1024)) + " kB")

        if tr_predict < threshold_1:
            new_limit = int(limit_cgroup * 0.9)
            change_limit_cgroup_file(str(new_limit))
            log_.debug("limit_cgroup - " + str(int(limit_cgroup / 1024)) + " kB")
            print(Style.BRIGHT + Fore.GREEN + "FREED MEMORY")
            write_output(round(self.t, 2), int(limit_cgroup) / 1048576, time_response, -1)

        elif threshold_1 < tr_predict < threshold_2 or self.tr_list.shape[0] < 1:
            print(Fore.YELLOW + "DO NOTHING")
            write_output(round(self.t, 2), int(limit_cgroup / 1048576), time_response, 0)

        else:
            new_limit = int(limit_cgroup * 2)
            change_limit_cgroup_file(str(new_limit))
            log_.debug("limit_cgroup - " + str(int(limit_cgroup / 1024)) + " kB")

            print(Style.BRIGHT + Fore.RED + "ADD MEMORY")
            write_output(round(self.t, 2), int(limit_cgroup / 1048576), time_response, 1)


if __name__ == "__main__":
    with open("out", "w") as f_out:
        f_out.write("")

    memorygetter = MemoryGetter()
    print("HOST? Mem used GB", memorygetter.get_mem_used() / 1048576)
    print("HOST? Mem used", memorygetter.get_mem_used())
    print("HOST? Mem proc", memorygetter.get_mem_proc())
    print("HOST? Limit cgroup", memorygetter.get_limit_cgroup())
    print("HOST? Swap used", memorygetter.get_swap_used())

    clientMemVm = ClientMemVM()
    print("4", clientMemVm)
    clientMemVm.connect()
    print("5")
    time.sleep(2)
    print("6")
    mechanism = Mechanism(memorygetter, clientMemVm)
    print("7", mechanism)
    mechanism.run()
    print("8")

cut_value = memory.current * 0.75
if RNN(cut_value) > THRESHOLD:
    memory.max *= 1.25
else:
    memory.max = cut_value
