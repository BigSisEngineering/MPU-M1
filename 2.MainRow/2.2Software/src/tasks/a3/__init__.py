import threading
import time

# -------------------------------------------------------- #
from src import components

# -------------------------------------------------------- #
from src._shared_variables import SV

print_name = "LOADER_M"

# -------------------------------------------------------- #
import requests
cage_list = [
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
]

class A3:
    def __init__(self):
        self._lock_accumulated_pots = threading.Lock()
        self._accumulated_pots = 0

        # -------------------------------------------------------- #
        self.loop_thread = threading.Thread(target=self._loop)

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
        return "Accumulated pots -> 0"



    def _loop(self):
        time_stamp = time.time() - 300  # set to 5 mins ago for instant 1st pulse

        while not SV.KILLER_EVENT.is_set():
            if time.time() - time_stamp > SV.PULSE_INTERVAL:
                if SV.run:
                    components.A3.start()
                    self._send_pulse()
                else:
                    components.A3.stop()

                time_stamp = time.time()

    def _get_num_pots(self):
        num_pots = 0
        for i in cage_list:
            try:
                url = f"http://cage0x00{i}.local:8080/potData"
                print(f'number of pots {num_pots} for {i}')
                num_pots += requests.get(url, timeout=(2, 10)).json()
            except Exception as e:
                print(f"The request of {url} - failed")

        print(f"num of pots needed for all: {num_pots}")
        return num_pots

    def _send_pulse(self):
        try:
            num_pots = self._get_num_pots()

            if components.A3.is_ready:
                # get leftovers from last pulse
                remaining = components.A3.get_remaining()

                # add [ current + accumulated + previously_not_sent ]
                _total_capsules = num_pots + self.accumulated_pots + remaining

                # reset accumulated
                self.set_zero()

                return components.A3.send_capsules(_total_capsules)

        except Exception as e:
            print("{:^10}-{:^15} Exception -> {}".format(print_name, "SEND PULSE", e))

        self.add_pots(num_pots)
        return False

    # -------------------------------------------------------- #
    def start(self):
        self.loop_thread.start()
