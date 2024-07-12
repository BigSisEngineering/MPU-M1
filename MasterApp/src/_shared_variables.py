from enum import Enum
import threading
from typing import Optional, Dict

# ------------------------------------------------------------------------------------ #
from src import setup

print_name = "SV"


class Duet(Enum):
    # A1 = f"192.168.83.100"
    # A2 = f"192.168.83.101"
    # A3 = f"192.168.83.102"
    # C1 = f"192.168.83.103"
    # C2 = f"192.168.83.104"
    A1 = f"10.207.1{setup.ROW}.11"
    A2 = f"10.207.1{setup.ROW}.12"
    A3 = f"10.207.1{setup.ROW}.13"
    C1 = f"10.207.1{setup.ROW}.14"
    C2 = f"10.207.1{setup.ROW}.15"


class Cages(Enum):
    CAGE01 = f"cage{setup.ROW-1}x0001"
    CAGE02 = f"cage{setup.ROW-1}x0002"
    CAGE03 = f"cage{setup.ROW-1}x0003"
    CAGE04 = f"cage{setup.ROW-1}x0004"
    CAGE05 = f"cage{setup.ROW-1}x0005"
    CAGE06 = f"cage{setup.ROW-1}x0006"
    CAGE07 = f"cage{setup.ROW-1}x0007"
    CAGE08 = f"cage{setup.ROW-1}x0008"
    CAGE09 = f"cage{setup.ROW-1}x0009"
    CAGE10 = f"cage{setup.ROW-1}x0010"
    CAGE11 = f"cage{setup.ROW-1}x0011"
    CAGE12 = f"cage{setup.ROW-1}x0012"
    CAGE13 = f"cage{setup.ROW-1}x0013"
    CAGE14 = f"cage{setup.ROW-1}x0014"


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

    BG_WATCHDOG = 4
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
