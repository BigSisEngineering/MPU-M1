from src.comm.http_duet import HTTPDuet

# -------------------------------------------------------- #
from src._shared_variables import Duet

print_name = "A3"


class PotDispenser(HTTPDuet):
    def __init__(self, duet: Duet = Duet.A3) -> None:
        self._duet_name = duet.name
        super().__init__(duet.value)

    @property
    def is_ready(self) -> bool:
        return (
            self.is_connected
            and (self.read_global("running") == 0)
            and (self.read_object("sensors.gpIn[0].value") == 0)
        )

    def get_remaining(self) -> int:
        remaining: int = 0
        try:
            remaining = self.read_global("remaining")
            self.set_global("remaining", 0)

        except Exception as e:
            print(
                "{:^10}-{:^15} Exception -> {}".format(print_name, self._duet_name, e)
            )

        return remaining

    def send_capsules(self, num_capsules: int) -> bool:
        try:
            if self.run_macro(
                macro_name="send_pots.g",
                param=f"A{num_capsules} B1",
            ):
                print(
                    "{:^10}-{:^15} Sending [{:^5}] capsules.".format(
                        print_name, self._duet_name, num_capsules
                    )
                )
                return True

        except Exception as e:
            print(
                "{:^10}-{:^15} Exception -> {}".format(print_name, self._duet_name, e)
            )

        return False

    # -------------------------------------------------------- #
    def start(self) -> None:
        if self.is_connected and self.read_global("run") == 0:
            print("{:^10}-{:^15} Start.".format(print_name, self._duet_name))
            self.run_macro("start.g")

    def stop(self) -> None:
        if self.is_connected and self.read_global("run") == 1:
            self.set_global("remaining", 0)  # reset remaining
            print("{:^10}-{:^15} Stop.".format(print_name, self._duet_name))
            self.run_macro("stop.g")
