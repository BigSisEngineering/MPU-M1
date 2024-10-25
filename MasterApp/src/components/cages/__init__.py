import time
import threading
from src.comm import http_cage
from typing import Dict

# -------------------------------------------------------- #
from src._shared_variables import SV

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "cage"

# -------------------------------------------------------- #
from src._shared_variables import Cages


class Cage(http_cage.HTTPCage):
    DEFAULT_STATUS = {
        "sensor_values": None,
        "star_wheel_status": None,
        "unloader_status": None,
        "mode": None,
    }

    def __init__(self, cage: Cages):
        super().__init__(cage.value)

        self._cage_name = cage.name

        # -------------------------------------------------------- #
        self._lock_status_ui = threading.Lock()
        self._status_ui: Dict = Cage.DEFAULT_STATUS

        # -------------------------------------------------------- #
        self._lock_maintainence_flag = threading.Lock()
        self._maintainence_flag = False

        threading.Thread(target=self._background_status_refresh).start()

    # PRIVATE
    # -------------------------------------------------------- #
    def _background_status_refresh(self):
        CLI.printline(
            Level.DEBUG,
            "({:^10})-({:^8}) BG ST REFRESH -> Start".format(print_name, self._cage_name),
        )

        time_stamp = time.time()

        while not SV.KILLER_EVENT.is_set():
            if (time.time() - time_stamp) > SV.BG_WATCHDOG:
                time_stamp = time.time()
                if not SV.UI_REFRESH_EVENT.is_set():
                    _status = self.status
                    if _status is not None:
                        self._w_status_ui(_status)
                    else:
                        self._w_status_ui(Cage.DEFAULT_STATUS)

        CLI.printline(
            Level.DEBUG,
            "({:^10})-({:^8}) BG ST REFRESH -> Stop".format(print_name, self._cage_name),
        )

    def _w_status_ui(self, w) -> None:
        with self._lock_status_ui:
            self._status_ui = w

    # PUBLIC
    # -------------------------------------------------------- #
    @property
    def status_ui(self) -> Dict:
        with self._lock_status_ui:
            _status = self._status_ui
        return _status

    @property
    def maintainence_flag(self) -> bool:
        with self._lock_maintainence_flag:
            _flag = self._maintainence_flag
        return _flag

    def set_maintainence_flag(self, w: str) -> str:
        _w = True if w == "true" else False

        with self._lock_maintainence_flag:
            self._maintainence_flag = w
        return f"Maintainence set to {w}"
