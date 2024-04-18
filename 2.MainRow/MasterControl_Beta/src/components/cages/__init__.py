import time
import threading
from src.comm.http_cage import HTTPCage, status_default
from typing import Dict

# -------------------------------------------------------- #
from src._shared_variables import SV

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "cage"

# -------------------------------------------------------- #
from src._shared_variables import Cages


class Cage(HTTPCage):
    def __init__(self, cage: Cages):
        super().__init__(cage.value)

        self._cage_name = cage.name

        # -------------------------------------------------------- #
        self._lock_status_ui = threading.Lock()
        self._status_ui = status_default

        threading.Thread(target=self._background_status_refresh).start()

    # PRIVATE
    # -------------------------------------------------------- #
    def _background_status_refresh(self):
        CLI.printline(
            Level.DEBUG,
            "({:^10})-({:^8}) BG ST REFRESH -> Start".format(
                print_name, self._cage_name
            ),
        )

        time_stamp = time.time()

        while not SV.KILLER_EVENT.is_set():
            if (time.time() - time_stamp) > SV.BG_WATCHDOG:
                if not SV.UI_REFRESH_EVENT.is_set():
                    _status = self.status
                    with self._lock_status_ui:
                        self._status_ui = _status

                time_stamp = time.time()
        CLI.printline(
            Level.DEBUG,
            "({:^10})-({:^8}) BG ST REFRESH -> Stop".format(
                print_name, self._cage_name
            ),
        )

    # PUBLIC
    # -------------------------------------------------------- #
    @property
    # for UI flush
    def status_ui(self) -> Dict:
        with self._lock_status_ui:
            _status = self._status_ui
        return _status

    # def refresh_status_ui(self) -> None:
    #     _status = self.status
    #     with self._lock_status_ui:
    #         self._status_ui = _status

    # @property
    # def ready(self) -> bool:
    #     status_dict = self.status
    #     if (
    #         status_dict["CONNECTED"]
    #         and status_dict["MODE"] == "PNP"
    #         and (
    #             status_dict["cageS"]["1"] != "Disconnected"
    #             and status_dict["cageS"]["1"] != "Camera fault"
    #         )
    #         and (
    #             status_dict["cageS"]["2"] != "Disconnected"
    #             and status_dict["cageS"]["2"] != "Camera fault"
    #         )
    #     ):
    #         return True
    #     return False

    # def start(self) -> str:
    #     self.set_mode("PNP")
    #     CLI.printline(
    #         Level.INFO,
    #         "({:^10})-({:^8}) Start PNP".format(print_name, self._cage_name),
    #     )
    #     return "({:^10})-({:^8}) Start PNP".format(print_name, self._cage_name)

    # def stop(self) -> str:
    #     self.set_mode("IDLE")
    #     CLI.printline(
    #         Level.INFO,
    #         "({:^10})-({:^8}) Stop PNP".format(print_name, self._cage_name),
    #     )
    #     return "({:^10})-({:^8}) Stop PNP".format(print_name, self._cage_name)
