import threading
import time

# -------------------------------------------------------- #
from src import components

# -------------------------------------------------------- #
from src._shared_variables import SV

print_name = "DIET_DSP"


class A2:
    def __init__(self):
        # -------------------------------------------------------- #
        self.loop_thread = threading.Thread(target=self._loop)

    def _loop(self):
        time_stamp = time.time() - 300  # set to 5 mins ago for instant 1st pulse

        while not SV.KILLER_EVENT.is_set():
            if time.time() - time_stamp > SV.WATCHDOG:
                components.A2.start() if SV.run_1a else components.A2.stop()

                time_stamp = time.time()

    # -------------------------------------------------------- #
    def start(self):
        print("{:^10} Start.".format(print_name))
        self.loop_thread.start()
