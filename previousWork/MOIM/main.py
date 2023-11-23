import time
import numpy as np
from threading import Thread
from log import Log
from memory_getter import MemoryGetter
from client_mem_vm import ClientMemVM
from apache_benchmark import Benchmark
from inferance import Inferance
from colorama import init, Fore, Back, Style

DURATION = 99999
FINESSE = 0.5
TR = 0
SUEIL_TR = 500

b = Benchmark()
log_ = Log()


def run_bench():
    global time_reponse
    time_reponse = 0
    while True:
        time_reponse = b.start_benchmark()


def change_limit_cgroup_file(cgroup_limit):
    with open(r"/sys/fs/cgroup/machine.slice/machine-qemu\x2d1\x2ddebian12\x2d1.scope/libvirt/memory.max", "w") as fmax:
        fmax.write(cgroup_limit)


def write_output(time, mem_limit, tr, action):
    with open("out", "a") as f_out:
        f_out.write("{},{},{},{}\n".format(time, mem_limit, tr, action))


class Mechanism:
    bash_tmp = []
    bash = []
    curr_tr_value = 0
    tr_list = np.zeros((0))
    t = 0
    coeff_first_seuil = 1.3
    coeff_second_seuil = 1.7

    def __init__(self, memorygetter, clientMemVm):
        self.memorygetter = memorygetter
        self.clientMemVm = clientMemVm
        self.infer = Inferance()

    def run(self):

        start_time = time.process_time()
        write_output("time", "mem_limit", "time_reponse", "action")

        self.t = round(time.process_time() - start_time, 2)
        Thread(target=run_bench).start()
        while self.t < DURATION:
            diff_t = round(time.process_time() - self.t - start_time, 2)
            if diff_t >= FINESSE and time_reponse > 0:  # we wait for the first value of the benchmark to perform an inference
                self.t += diff_t
                self.update_bash()
                self.do_inferance()
                print(Style.BRIGHT + Fore.GREEN + "[t = {} s]".format(int(self.t)), end="\r")

    def add_tr_to_list_tr(self, tr):
        if self.tr_list.shape[0] < 10 and tr != 0:
            self.tr_list = np.append(self.tr_list, tr)
        elif tr != 0:
            self.tr_list = np.roll(self.tr_list, -1)
            self.tr_list[-1] = tr

    def SEUIL(self):
        seuil1, seuil2 = np.mean(self.tr_list) * self.coeff_first_seuil, np.mean(self.tr_list) * self.coeff_second_seuil
        log_.debug("SEUIL1 = {} - SEUIL2={}".format(seuil1, seuil2))
        log_.debug(self.tr_list)
        return seuil1, seuil2

    def update_bash(self):
        if np.array(self.bash_tmp).shape[0] < 25:
            self.bash_tmp.append([
                self.memorygetter.get_mem_proc() / 1048576,
                self.clientMemVm.get_value() / 1024,
                self.memorygetter.get_limit_cgroup() / 1048576,
                time_reponse
            ])
        else:
            self.bash = self.bash_tmp
            self.bash_tmp = []

    def do_inferance(self):
        # we do prediction only when we have a new time reponse value
        # that prevent us to cut lower the cgroup limit too frequently and make a prediction with tr value that are not descriptive of the VM state
        if self.curr_tr_value != time_reponse and np.array(self.bash).shape[0] == 25:
            self.add_tr_to_list_tr(self.curr_tr_value)
            self.do_predict()
            self.curr_tr_value = time_reponse

    def do_predict(self):
        x_bash = np.array([self.bash])
        x_bash[0, :, -1] = time_reponse
        tr_predict = self.infer.predict(x_bash)
        log_.output("(tr predict is - " + str(tr_predict[0]) + ") (tr current is - " + str(self.curr_tr_value) + ")")
        self.change_limit_cgroup(tr_predict[0])

    def change_limit_cgroup(self, tr_predict):

        seuil1, seuil2 = self.SEUIL()

        if tr_predict < seuil1:
            new_limit = int(self.memorygetter.get_limit_cgroup() * 0.9)
            change_limit_cgroup_file(str(new_limit))
            log_.debug("limit_cgroup - " + str(int(self.memorygetter.get_limit_cgroup() / 1024)) + " kB")
            print(Style.BRIGHT + Fore.GREEN + "FREED MEMORY")
            write_output(round(self.t, 2), int(self.memorygetter.get_limit_cgroup()) / 1048576, time_reponse, -1)

        elif seuil1 < tr_predict < seuil2 or self.tr_list.shape[0] < 1:
            print(Fore.YELLOW + "DO NOTHING")
            write_output(round(self.t, 2), int(self.memorygetter.get_limit_cgroup() / 1048576), time_reponse, 0)

        else:

            new_limit = int(self.memorygetter.get_limit_cgroup() * 2)
            change_limit_cgroup_file(str(new_limit))
            log_.debug("limit_cgroup - " + str(int(self.memorygetter.get_limit_cgroup() / 1024)) + " kB")

            print(Style.BRIGHT + Fore.RED + "ADD MEMORY")
            write_output(round(self.t, 2), int(self.memorygetter.get_limit_cgroup() / 1048576), time_reponse, 1)


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

# cut_value = memory.current * 0.75
# if RNN(cut_value) > SUEIL:
#    memory.max *= 1.25
# else:
#    memory.max = cut_value
