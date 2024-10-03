import threading
import time

# ------------------------------------------------------------------------------------ #
from src import components

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "DIET_DSP"

# ------------------------------------------------------------------------------------ #
from src._shared_variables import SV


class A2:
    def __init__(self):
        # ------------------------------------------------------------------------------------ #
        self.loop_thread = threading.Thread(target=self._loop)
        self._create_fresh_session: bool = True

    def _loop(self):
        time_stamp = time.time() - 300  # set to 5 mins ago for instant 1st pulse

        while not SV.KILLER_EVENT.is_set():
            if time.time() - time_stamp > SV.WATCHDOG:
                components.A2.start() if SV.run_1a else components.A2.stop()

                time_stamp = time.time()
        CLI.printline(Level.INFO, "({:^10}) End".format(print_name))

    # ------------------------------------------------------------------------------------ #
    def start(self):
        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))
        self.loop_thread.start()
