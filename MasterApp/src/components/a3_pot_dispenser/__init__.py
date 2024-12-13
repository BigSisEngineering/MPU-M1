from dataclasses import dataclass, asdict, field

from src.comm.http_duet import HTTPDuet
from src._shared_variables import Duet

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "A3"


class Sensors:
    BUFF_IN = 0
    POT_PRESENCE = 1
    SW_ERROR = 2


class GlobalVars:
    RUN = "run"
    IS_RUNNING = "running"
    SW_HOMED = "sw_homed"
    REMAINING = "remaining"


@dataclass
class Status:
    connected: bool = field(default=False)
    running: bool = field(default=False)
    sw_error: bool = field(default=False)
    sw_homed: bool = field(default=False)
    buff_in: bool = field(default=False)
    pot_sensor: bool = field(default=False)

    def dict(self):
        return {k: v for k, v in asdict(self).items()}


class API(HTTPDuet):
    def __init__(self, duet: Duet = Duet.A3) -> None:
        self._duet_name = duet.name
        super().__init__(duet.value)

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

    def reset_remaining(self) -> bool:
        return self.set_global(GlobalVars.REMAINING, 0)

    def start(self) -> None:
        if self.run_macro("start.g"):
            CLI.printline(Level.INFO, "{:^10}-{:^15} Start.".format(print_name, self._duet_name))

    def stop(self) -> None:
        if self.run_macro("stop.g"):
            CLI.printline(Level.INFO, "{:^10}-{:^15} Stop.".format(print_name, self._duet_name))

    def sw_ack_fault(self) -> str:
        if self.run_macro("sw_clear_fault.g"):
            return "{} SW clear fault.".format(print_name)
        return "{} SW clear fault failed.".format(print_name)

    def sw_home(self) -> str:
        if self.run_macro("sw_clear_fault.g") and self.run_macro("sw_home.g"):
            return "{} SW home.".format(print_name)
        return "{} SW home failed.".format(print_name)
