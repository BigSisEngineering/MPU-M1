from dataclasses import dataclass, asdict, field

from src.comm.http_duet import HTTPDuet
from src._shared_variables import Duet, SV

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "C2"


class Sensors:
    POT_PRESENCE = 1
    CHIMNEY_PRESENCE = 0


@dataclass
class Status:
    connected: bool = field(default=False)
    running: bool = field(default=False)
    pot_sensor: bool = field(default=False)
    chimney_sensor: bool = field(default=False)

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


class API(HTTPDuet):
    def __init__(self, duet: Duet = Duet.C2) -> None:
        self._duet_name = duet.name
        super().__init__(duet.value)

    def start(self):
        if self.run_macro("run.g"):
            CLI.printline(Level.INFO, "{:^10}-{:^15} Start.".format(print_name, self._duet_name))

    def stop(self):
        if self.abort():
            CLI.printline(Level.INFO, "{:^10}-{:^15} Stop.".format(print_name, self._duet_name))
