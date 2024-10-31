import threading
import requests
import time
from typing import List

# -------------------------------------------------------- #
from src import components

# -------------------------------------------------------- #
from src._shared_variables import SV, Cages

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "POT DISP"


class A3:
    def __init__(self):
        self._lock_accumulated_pots = threading.Lock()
        self._accumulated_pots: int = 0
        self._set_zero_flag: bool = False

        #
        self.lock_num_pots = threading.Lock()
        self.num_pots: int = 0

        # -------------------------------------------------------- #
        self.loop_thread = threading.Thread(target=self._loop)

    # ------------------------------------------------------------------------------------ #
    @property
    def accumulated_pots(self) -> int:
        with self._lock_accumulated_pots:
            _accumulated_pots = self._accumulated_pots
        return _accumulated_pots

    def add_pots(self, w: int) -> str:
        with self._lock_accumulated_pots:
            self._accumulated_pots = self._accumulated_pots + w
        return "Added {:^3} pots".format(w)

    def set_zero(self) -> str:
        with self._lock_accumulated_pots:
            self._accumulated_pots = 0

        self._set_zero_flag = True
        return f"Accumulated pots -> 0."

    # ------------------------------------------------------------------------------------ #
    def _loop(self) -> None:
        time_stamp = time.time() - 300  # set to 5 mins ago for instant 1st pulse

        while not SV.KILLER_EVENT.is_set():
            if time.time() - time_stamp > SV.PULSE_INTERVAL:
                if SV.run_1a:
                    components.A3.start()
                    if self._send_pulse():
                        time_stamp = time.time()
                else:
                    components.A3.stop()
        CLI.printline(Level.INFO, "({:^10}) End".format(print_name))

    # ------------------------------------------------------------------------------------ #
    def _get_pot_cage(self, cage) -> None:
        result = components.cage_dict[cage].fetch_pot_data()
        with self.lock_num_pots:
            self.num_pots += result

    def _get_num_pots(self) -> int:
        threads: List[threading.Thread] = []
        for cage in Cages:
            threads.append(threading.Thread(target=self._get_pot_cage, args=(cage,)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        with self.lock_num_pots:
            num_pots = self.num_pots
            self.num_pots = 0

        return num_pots

    def _send_pulse(self) -> bool:
        try:
            num_pots = self._get_num_pots()

            if components.A3.is_ready:
                # get leftovers from last pulse
                remaining = components.A3.get_remaining()

                if self._set_zero_flag:  # reset
                    remaining = 0
                    self._set_zero_flag = False

                # add [ current + accumulated + previously_not_sent ]
                _total_capsules = num_pots + self.accumulated_pots + remaining

                # reset accumulated
                with self._lock_accumulated_pots:
                    self._accumulated_pots = 0

                if components.A3.send_capsules(_total_capsules):
                    return True
                else:
                    with self._lock_accumulated_pots:
                        self._accumulated_pots += num_pots  # add pots if not executed

        except Exception as e:
            CLI.printline(Level.ERROR, "{:^10}-{:^15} Exception -> {}".format(print_name, "SEND PULSE", e))

        return False

    # -------------------------------------------------------- #
    def start(self) -> None:
        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))
        self.loop_thread.start()
