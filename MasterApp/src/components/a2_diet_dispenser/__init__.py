from dataclasses import dataclass, asdict
from typing import Dict
import time
import threading

# ------------------------------------------------------------------------------------ #
from src.comm.http_duet import HTTPDuet

# ------------------------------------------------------------------------------------ #
from src._shared_variables import Duet, SV

# ------------------------------------------------------------------------------------ #
from src import data

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "A2"


@dataclass
class Data:
    connected: bool
    running: bool
    dispenser_homed: bool
    sw_error: bool
    sw_homed: bool
    buff_in: bool
    buff_out: bool
    pot_sensor: bool

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


class DietDispenser(HTTPDuet):
    def __init__(self, duet: Duet = Duet.A2) -> None:
        self._duet_name = duet.name
        super().__init__(duet.value)

        # ------------------------------------------------------------------------------------ #
        self._lock_status_ui = threading.Lock()
        self._status_ui: Dict = Data(False, False, False, False, False, False, False, False).dict()

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
        return self.is_connected and self.read_global("flag_sw_homing") == 0

    @property
    def status(self) -> Dict:
        data: Data = Data(
            connected=self.is_connected,
            running=True if self.read_global("run") == 1 and self.is_connected else False,
            dispenser_homed=True if self.read_global("flag_dispenser_homed") == 1 else False,
            sw_error=True if self.read_object("sensors.gpIn[3].value") == 1 else False,
            sw_homed=True if self.read_global("sw_homed") == 1 else False,
            buff_in=True if self.read_object("sensors.gpIn[0].value") == 1 else False,
            buff_out=True if self.read_object("sensors.gpIn[1].value") == 1 else False,
            pot_sensor=True if self.read_object("sensors.gpIn[2].value") == 1 else False,
        )
        return data.dict()

    @property
    def status_ui(self) -> Dict:
        with self._lock_status_ui:
            _status_ui = self._status_ui
        return _status_ui

    def _get_pots_dispensed(self) -> int:
        if self.is_ready:
            return self.read_global("pots_dispensed")
        return 0

    def _update_data(self) -> None:
        pots_dispensed = self.read_global("pots_dispensed")
        if isinstance(pots_dispensed, int):
            data.A2.update_data(pots_dispensed)
        else:
            CLI.printline(
                Level.WARNING,
                "{:^10}-{:^15} Update data failed -> Invalid data.".format(print_name, self._duet_name),
            )

    def start(self) -> bool:
        if self.is_ready:
            run = self.read_global("run")
            if run == 0:
                if self.set_global("pots_dispensed", 0) and self.set_global("run", 1):
                    data.A2.create_session()  # create new session
                    CLI.printline(Level.INFO, "{:^10}-{:^15} Start.".format(print_name, self._duet_name))
                    return True

            elif run == 1:
                self._update_data()  # update data
        else:
            CLI.printline(Level.WARNING, "{:^10}-{:^15} Start failed.".format(print_name, self._duet_name))
        return False

    def stop(self) -> bool:
        if self.is_ready and self.read_global("run") == 1:
            if self.set_global("run", 0):
                self._update_data()  # final update
                CLI.printline(Level.INFO, "{:^10}-{:^15} Stop.".format(print_name, self._duet_name))
        return False

    def reposition_nozzle(self) -> bool:
        if self.is_ready and self.read_global("flag_reposition_nozzle") == 0:
            if self.set_global("flag_reposition_nozzle", 1):
                CLI.printline(Level.INFO, "{:^10}-{:^15} Reposition nozzle.".format(print_name, self._duet_name))
                return True
        CLI.printline(Level.WARNING, "{:^10}-{:^15} Reposition nozzle failed.".format(print_name, self._duet_name))
        return False

    def raise_nozzle(self) -> bool:
        if self.is_ready and self.read_global("flag_raise_nozzle") == 0:
            if self.set_global("flag_raise_nozzle", 1):
                CLI.printline(Level.INFO, "{:^10}-{:^15} Raise nozzle.".format(print_name, self._duet_name))
                return True
        CLI.printline(Level.WARNING, "{:^10}-{:^15} Raise nozzle failed.".format(print_name, self._duet_name))
        return False

    def sw_ack_fault(self) -> bool:
        if self.is_ready:
            if self.set_global("flag_sw_clear_fault", 1):
                CLI.printline(Level.INFO, "{:^10}-{:^15} SW clear fault.".format(print_name, self._duet_name))
                return True
        CLI.printline(Level.WARNING, "{:^10}-{:^15} SW clear fault failed.".format(print_name, self._duet_name))
        return False

    def sw_home(self) -> bool:
        if self.is_ready:
            if self.set_global("flag_sw_home", 1):
                CLI.printline(Level.INFO, "{:^10}-{:^15} SW home.".format(print_name, self._duet_name))
                return True
        CLI.printline(Level.WARNING, "{:^10}-{:^15} SW home failed.".format(print_name, self._duet_name))
        return False


def debug():
    obj = DietDispenser()
    print(obj.read_object("sensors"))
