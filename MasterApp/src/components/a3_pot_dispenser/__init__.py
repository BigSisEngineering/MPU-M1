from dataclasses import dataclass, asdict
from typing import Dict
import time
import threading

# ------------------------------------------------------------------------------------ #
from src.comm.http_duet import HTTPDuet
from src._shared_variables import Duet, SV

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "A3"


@dataclass
class Data:
    connected: bool
    running: bool
    sw_error: bool
    sw_homed: bool
    buff_in: bool
    pot_sensor: bool

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


class PotDispenser(HTTPDuet):
    def __init__(self, duet: Duet = Duet.A3) -> None:
        self._duet_name = duet.name
        super().__init__(duet.value)

        # ------------------------------------------------------------------------------------ #
        self._lock_status_ui = threading.Lock()
        self._status_ui: Dict = Data(False, False, False, False, False, False).dict()

        threading.Thread(target=self._background_status_refresh).start()

    def _background_status_refresh(self):
        CLI.printline(
            Level.DEBUG,
            "({:^10})-({:^8}) BG ST REFRESH -> Start".format(print_name, self._duet_name),
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
            "({:^10})-({:^8}) BG ST REFRESH -> Stop".format(print_name, self._duet_name),
        )

    @property
    def is_ready(self) -> bool:
        return (
            self.is_connected
            and (self.read_global("running") == 0)
            and (self.read_object("sensors.gpIn[0].value") == 0)
        )

    @property
    def status(self) -> Dict:
        data: Data = Data(
            self.is_connected,
            True if (self.is_connected and SV.run_1a) else False,
            True if self.read_object("sensors.gpIn[0].value") == 1 else False,
            True if self.read_object("sensors.gpIn[1].value") == 1 else False,
            True if self.read_object("sensors.gpIn[2].value") == 1 else False,
            True if self.read_global("sw_homed") == 1 else False,
        )
        return data.dict()

    @property
    def status_ui(self) -> Dict:
        with self._lock_status_ui:
            _status_ui = self._status_ui
        return _status_ui

    def get_remaining(self) -> int:
        remaining: int = 0
        try:
            remaining = self.read_global("remaining")
            self.set_global("remaining", 0)

        except Exception as e:
            CLI.printline(Level.ERROR, "{:^10}-{:^15} Exception -> {}".format(print_name, self._duet_name, e))

        return remaining

    def send_capsules(self, num_capsules: int) -> bool:
        try:
            if self.run_macro(
                macro_name="send_pots.g",
                param=f"A{num_capsules}",
            ):
                CLI.printline(
                    Level.INFO,
                    "{:^10}-{:^15} Sending [{:^5}] capsules.".format(print_name, self._duet_name, num_capsules),
                )
                return True

        except Exception as e:
            CLI.printline(Level.ERROR, "{:^10}-{:^15} Exception -> {}".format(print_name, self._duet_name, e))

        return False

    # -------------------------------------------------------- #
    def start(self) -> None:
        if self.is_connected and self.read_global("run") == 0:
            CLI.printline(Level.INFO, "{:^10}-{:^15} Start.".format(print_name, self._duet_name))
            self.run_macro("start.g")

    def stop(self) -> None:
        if self.is_connected and self.read_global("run") == 1:
            self.set_global("remaining", 0)  # reset remaining
            CLI.printline(Level.INFO, "{:^10}-{:^15} Stop.".format(print_name, self._duet_name))
            self.run_macro("stop.g")

    def sw_ack_fault(self) -> bool:
        if self.is_ready:
            CLI.printline(Level.INFO, "{:^10}-{:^15} SW clear fault.".format(print_name, self._duet_name))
            return self.run_macro("sw_clear_fault.g")
        return False

    def sw_home(self) -> bool:
        if self.is_ready:
            CLI.printline(Level.INFO, "{:^10}-{:^15} SW home.".format(print_name, self._duet_name))
            return self.run_macro("sw_home.g")
        return False
