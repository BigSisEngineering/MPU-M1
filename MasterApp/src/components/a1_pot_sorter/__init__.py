import time
from typing import Dict
from dataclasses import dataclass, asdict
import threading

# -------------------------------------------------------- #
from src.comm.http_duet import HTTPDuet
from src._shared_variables import Duet, SV

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "A1"


@dataclass
class Data:
    connected: bool
    running: bool
    buff_out: bool

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


class PotSorter(HTTPDuet):
    def __init__(self, duet: Duet = Duet.A1) -> None:
        self._duet_name = duet.name
        super().__init__(duet.value)

        # ------------------------------------------------------------------------------------ #
        self._lock_status_ui = threading.Lock()
        self._status_ui: Dict = Data(False, False, False).dict()

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
        return self.is_connected

    @property
    def status(self) -> Dict:
        data: Data = Data(
            self.is_connected,
            True if not self.is_idle and self.is_connected else False,
            True if self.read_object("sensors.gpIn[0].value") == 1 and self.is_connected else False,
        )
        return data.dict()

    @property
    def status_ui(self) -> Dict:
        with self._lock_status_ui:
            _status_ui = self._status_ui
        return _status_ui

    def start(self):
        if self.is_ready and self.is_idle:
            self.run_macro("run.g")
            CLI.printline(Level.INFO, "{:^10}-{:^15} Start.".format(print_name, self._duet_name))

    def stop(self):
        if self.is_ready and not self.is_idle:
            self.abort()
            CLI.printline(Level.INFO, "{:^10}-{:^15} Stop.".format(print_name, self._duet_name))
