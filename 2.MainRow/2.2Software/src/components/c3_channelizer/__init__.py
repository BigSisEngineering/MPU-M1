from src.comm.http_duet import HTTPDuet

# -------------------------------------------------------- #
from src._shared_variables import Duet

print_name = "C3"


class Channelizer(HTTPDuet):
    def __init__(self, duet: Duet = Duet.C3) -> None:
        self._duet_name = duet.name
        super().__init__(duet.value)

    @property
    def is_ready(self) -> bool:
        return self.is_connected

    def start(self):
        if self.is_ready and self.read_global("run") == 0:
            print("{:^10}-{:^15} Start.".format(print_name, self._duet_name))
            self.set_global("run", 1)

    def stop(self):
        if self.is_ready and self.read_global("run") == 1:
            print("{:^10}-{:^15} Stop.".format(print_name, self._duet_name))
            self.set_global("run", 0)
