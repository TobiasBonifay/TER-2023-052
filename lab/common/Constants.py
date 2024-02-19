from lab.common.config_loader import load_config

try:
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
    PCAP_FILE = CONFIG["PCAP_FILE"]
except KeyError as e:
    print(f"Error loading config: {e}")
except FileNotFoundError as e:
    print(f"Error loading config: {e}")
    pass

BANDWIDTH_UPLOAD_VM_ = 'VM2 VIEW Bandwidth Upload'
BANDWIDTH_DOWNLOAD_VM_ = 'VM2 VIEW Bandwidth Download'
RESPONSE_TIME_VM_ = 'VM2 VIEW Response Time'
SWAP_HOST_ = 'HOST VIEW VM Current Swap'
MEMORY_HOST_ = 'HOST VIEW VM Memory used'
MEMORY_AVAILABLE_VM_ = 'VM VIEW Memory Available'
MEMORY_USED_VM_ = 'VM VIEW Memory Used'
MEMORY_TOTAL_VM_ = 'VM VIEW Memory Total'
C_GROUP_LIMIT_VM_ = 'VM VIEW Current CGroup Limit'
ACTION_TAKEN = 'Action Taken'
TIME = 'Time'

SCENARIOS = [(1024, 60), (768, 60), (512, 60), (256, 60), (1024, 60)]
