from dataclasses import dataclass, asdict, field

# -------------------------------------------------------- #
from src.comm.http_duet import HTTPDuet
from src._shared_variables import Duet, SV

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "A1"


class Sensors:
    BUFF_OUT = 0


@dataclass
class Status:
    connected: bool = field(default=False)
    running: bool = field(default=False)
    buff_out: bool = field(default=False)

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


class API(HTTPDuet):
    def __init__(self, duet: Duet = Duet.A1) -> None:
        self._duet_name = duet.name
        super().__init__(duet.value)

    def start(self):
        if self.run_macro("run.g"):
            CLI.printline(Level.INFO, "{:^10}-{:^15} Start.".format(print_name, self._duet_name))

    def stop(self):
        if self.abort():
            CLI.printline(Level.INFO, "{:^10}-{:^15} Stop.".format(print_name, self._duet_name))
