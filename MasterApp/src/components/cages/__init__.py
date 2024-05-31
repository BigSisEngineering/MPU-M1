import time
import threading
from src.comm.http_cage import HTTPCage
from dataclasses import dataclass, asdict
from typing import Dict, Any

# -------------------------------------------------------- #
from src._shared_variables import SV

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "cage"

# -------------------------------------------------------- #
from src._shared_variables import Cages


@dataclass
class Data:
    sensors_values: Any
    star_wheel_status: Any
    unloader_status: Any
    mode: Any

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


class Cage(HTTPCage):
    def __init__(self, cage: Cages):
        super().__init__(cage.value)

        self._cage_name = cage.name

        # -------------------------------------------------------- #
        self._lock_status_ui = threading.Lock()
        self._status_ui: Dict = Data(None, None, None, None).dict()

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
                if not SV.UI_REFRESH_EVENT.is_set():
                    _status = self.status
                    if _status is not None:
                        with self._lock_status_ui:
                            self._status_ui = _status

                time_stamp = time.time()
        CLI.printline(
            Level.DEBUG,
            "({:^10})-({:^8}) BG ST REFRESH -> Stop".format(print_name, self._cage_name),
        )

    # PUBLIC
    # -------------------------------------------------------- #
    @property
    def status_ui(self) -> Dict:
        with self._lock_status_ui:
            _status = self._status_ui
        return _status
