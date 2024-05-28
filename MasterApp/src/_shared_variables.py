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
        self._run_1a = False
        self._lock_run_1a = threading.Lock()

        self._run_1c = False
        self._lock_run_1c = threading.Lock()

        self.is1AActive = False
        self.is1CActive = False

    # -------------------------------------------------------- #
    @property
    def run_1a(self) -> bool:
        with self._lock_run_1a:
            _run_1a = self._run_1a
        return _run_1a

    def w_run_1a(self, w: bool) -> str:
        with self._lock_run_1a:
            self._run_1a = w
        return "{:^10} RUN 1A -> {}".format(print_name, w)

    @property
    def run_1c(self) -> bool:
        with self._lock_run_1c:
            _run_1c = self._run_1c
        return _run_1c

    def w_run_1c(self, w: bool) -> str:
        with self._lock_run_1c:
            self._run_1c = w
        return "{:^10} RUN 1C -> {}".format(print_name, w)


SV = SharedVariables()
