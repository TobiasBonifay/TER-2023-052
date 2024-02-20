import threading
import time

TO_MEGA = 1024 * 1024


class ScenarioManager:
    def __init__(self, cgroup_manager, scenarios, callback):
        self.thread = None
        self.cgroup_manager = cgroup_manager
        self.scenarios = scenarios
        self.callback = callback
        self.stop_event = threading.Event()

    def start(self):
        self.thread = threading.Thread(target=self.run_scenarios)
        self.thread.start()

    def run_scenarios(self):
        for i, (limit, duration) in enumerate(self.scenarios):
            if self.stop_event.is_set():
                break
            self.callback('start', i)
            self.cgroup_manager.change_cgroup_limit_vm(limit * TO_MEGA)
            time.sleep(duration)
            self.callback('end', i)
        self.callback('complete', len(self.scenarios))

    def stop(self):
        self.stop_event.set()
        self.thread.join()

    def is_done(self):
        return self.stop_event.is_set()
