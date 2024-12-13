from dataclasses import dataclass, asdict, field

# ------------------------------------------------------------------------------------ #
from src.comm.http_duet import HTTPDuet
from src._shared_variables import Duet

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "A2"


class Sensors:
    BUFF_IN = 0
    BUFF_OUT = 1
    POT_PRESENCE = 2
    SW_ERROR = 3


class GlobalVars:
    RUN = "run"
    SW_HOMED = "sw_homed"
    DISPENSER_HOMED = "flag_dispenser_homed"
    POTS_DISPENSED = "pots_dispensed"
    SW_HOMING = "flag_sw_homing"
    REQUEST_REPOSITION_NOZZLE = "flag_reposition_nozzle"
    REQUEST_RAISE_NOZZLE = "flag_raise_nozzle"
    REQUEST_SW_CLEAR_FAULT = "flag_sw_clear_fault"
    REQUEST_SW_HOME = "flag_sw_home"


@dataclass
class Status:
    connected: bool = field(default=False)
    running: bool = field(default=False)
    dispenser_homed: bool = field(default=False)
    sw_error: bool = field(default=False)
    sw_homed: bool = field(default=False)
    buff_in: bool = field(default=False)
    buff_out: bool = field(default=False)
    pot_sensor: bool = field(default=False)

    def dict(self):
        return {k: v for k, v in asdict(self).items()}


class API(HTTPDuet):
    def __init__(self, duet: Duet = Duet.A2) -> None:
        self._duet_name = duet.name
        super().__init__(duet.value)

    def start(self) -> bool:
        return self.set_global(GlobalVars.RUN, 1)

    def stop(self) -> bool:
        return self.set_global(GlobalVars.RUN, 0)

    def reset_pots_dispensed(self) -> bool:
        return self.set_global(GlobalVars.POTS_DISPENSED, 0)

    def reposition_nozzle(self) -> str:
        if self.set_global(GlobalVars.REQUEST_REPOSITION_NOZZLE, 1):
            return "{} -> Reposition Nozzle".format(print_name)
        return "{} -> Reposition Nozzle Failed".format(print_name)

    def raise_nozzle(self) -> str:
        if self.set_global(GlobalVars.REQUEST_RAISE_NOZZLE, 1):
            return "{} -> Raise Nozzle".format(print_name)
        return "{} -> Raise Nozzle Failed".format(print_name)

    def sw_ack_fault(self) -> str:
        if self.set_global(GlobalVars.REQUEST_SW_CLEAR_FAULT, 1):
            return "{} -> ACK starwheel fault".format(print_name)
        return "{} -> ACK starwheel fault Failed".format(print_name)

    def sw_home(self) -> str:
        if self.set_global(GlobalVars.REQUEST_SW_HOME, 1):
            return "{} -> Home starwheel".format(print_name)
        return "{} -> Home starwheel Failed".format(print_name)
