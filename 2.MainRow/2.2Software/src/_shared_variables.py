from enum import Enum
import threading

print_name = "SV"


class Duet(Enum):
    A1 = "192.168.83.100"
    A2 = "192.168.83.101"
    A3 = "192.168.83.102"
    C1 = "192.168.83.103"
    C2 = "192.168.83.104"


class SharedVariables:
    WATCHDOG = 1
    KILLER_EVENT = threading.Event()
    PULSE_INTERVAL = 2.5  # seconds
    TASK_THREAD_STARTED = False

    # todo: A1, A2 pause event

    def __init__(self) -> None:
        self._run = False
        self._lock_run = threading.Lock()

    # -------------------------------------------------------- #
    @property
    def run(self) -> bool:
        with self._lock_run:
            _run = self._run
        return _run

    def w_run(self, w: bool) -> str:
        with self._lock_run:
            self._run = w
        return "{:^10} RUN -> {}".format(print_name, w)


SV = SharedVariables()
