from lab.common.config_loader import load_config

CONFIG = load_config()

FINESSE = CONFIG["FINESSE"]
MIN_CGROUP_LIMIT = CONFIG["MIN_CGROUP_LIMIT"]
HOST_PATH_CGROUP_FILE = CONFIG["HOST_PATH_CGROUP_FILE"]
VM1_PATH_CGROUP_FILE = CONFIG["VM1_PATH_CGROUP_FILE"]
VM1_IP = CONFIG["VM1_IP"]
VM1_PORT = CONFIG["VM1_PORT"]
VM2_IP = CONFIG["VM2_IP"]
VM2_PORT = CONFIG["VM2_PORT"]
DURATION = CONFIG["DURATION"]
MODEL_PATH = CONFIG["MODEL_PATH"]
CSV_FILE = CONFIG["CSV_FILE"]
RUNTIME_ACTIONS_FILE = CONFIG["RUNTIME_ACTIONS_FILE"]
THRESHOLD_1 = CONFIG["THRESHOLD_1"]
THRESHOLD_2 = CONFIG["THRESHOLD_2"]
INTERFACE = CONFIG["INTERFACE"]
