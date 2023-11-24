import re
from subprocess import PIPE, run

MOTIF_RE_FLOAT = r"\d+"


class Benchmark:

    def __init__(self):
        pass

    @staticmethod
    def start_benchmark():
        """
        Start apache benchmark and return the longest request time
        :return:
        """
        res_time = 0
        print("Starting apache benchmark")
        # check if apache benchmark is installed
        if run("which ab", stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True).returncode != 0:
            print("Apache benchmark is not installed")
            exit(1)
        else:
            print("Apache benchmark is installed")

        # run apache benchmark
        benchmark_cmd = "ab -n 1000 -c 100 http://192.168.100.175:80/"

        result = run(benchmark_cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        if result.returncode != 0:
            print("Error while running apache benchmark")
            exit(1)

        for l in result.stdout.splitlines():
            if "(longest request)" in l:
                res_time = int(re.findall(MOTIF_RE_FLOAT, l)[1])
                break

        return res_time
