from enum import Enum
from typing import Optional, Dict
import threading

print_name = "SV"


class Duet(Enum):
    A1 = "192.168.83.100"
    A2 = "192.168.83.101"
    A3 = "192.168.83.102"
    C1 = "192.168.83.103"
    C2 = "192.168.83.104"
    C3 = "192.168.83.105"


class Cages(Enum):
    CAGE01 = "cage0x0001"
    CAGE02 = "cage0x0002"
    CAGE03 = "cage0x0003"
    CAGE04 = "cage0x0004"
    CAGE05 = "cage0x0005"
    CAGE06 = "cage0x0006"
    CAGE07 = "cage0x0007"
    CAGE08 = "cage0x0008"
    CAGE09 = "cage0x0009"
    CAGE10 = "cage0x0010"
    CAGE11 = "cage0x0011"
    CAGE12 = "cage0x0012"
    CAGE13 = "cage0x0013"
    CAGE14 = "cage0x0014"
    CAGE15 = "cage0x0015"


# -------------------------------------------------------- #
class Mode(Enum):
    pnp_mode = 0
    dummy_mode = 1
    idle = 2
    offline = 3


class Status(Enum):
    normal = 0
    slot_empty = 1
    error = 2
    offline = 3
    not_init = 4


cage_mode_dict: Optional[Dict[Cages, Mode]] = {}
cage_status_dict: Optional[Dict[Cages, Status]] = {}

for cage in Cages:
    cage_mode_dict[cage] = Mode.offline
    cage_status_dict[cage] = Status.offline
# -------------------------------------------------------- #


class SharedVariables:
    WATCHDOG = 1
    KILLER_EVENT = threading.Event()
    PULSE_INTERVAL = 2.5  # seconds
    THREAD_STARTED = False

    BG_WATCHDOG = 5
    UI_REFRESH_EVENT = threading.Event()

    last_update_time = "------"

    # todo: A1, A2 pause event

    def __init__(self) -> None:
        self._run_1a = False
        self._lock_run_1a = threading.Lock()

        self._run_1c = False
        self._lock_run_1c = threading.Lock()

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
