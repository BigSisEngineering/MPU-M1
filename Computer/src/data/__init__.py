import threading
from src import setup
from dataclasses import dataclass, asdict
import time

# ------------------------------------------------------------------------------------------------ #

lock: threading.Lock = threading.Lock()
# board_data: dict = dict()
pnp_data: dict = dict()


@dataclass
class PNPData:
    started_time: time.ctime
    is_first_pnp: bool
    got_egg_in_pot: bool
    pot_processed: int
    egg_pot_detected: int
    detection: bool
    number_of_egg_pot_since_last_ask: int
    pnp_confidence: int
    cycle_time: float

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


pnp_data_lock = threading.Lock()
pnp_vision_lock = threading.Lock()
pnp_data: PNPData = PNPData(
    0,
    True,
    False,
    pot_processed=0,
    egg_pot_detected=0,
    detection=False,
    number_of_egg_pot_since_last_ask=0,
    pnp_confidence=80,
    cycle_time=3.0,
)

is_star_wheel_error: bool = False
is_unloader_error: bool = False
max_auto_clear_error = 3

servos_ready: bool = False
sw_homing: bool = False

star_wheel_duration_ms: int = 600
sw_pos: int = 0

dummy_enabled: bool = False
unload_probability: float = 1.0

pnp_enabled: bool = False
pnp_confidence: float = 0.80

experiment_enabled: bool = False
experiment_pause_interval = 600.0
experiment_pause_start_time = None
experiment_pause_state = False
experiment_status = ""

MongoDB_INIT: bool = False

pot_processed: int = 0
pot_unloaded: int = 0
pot_unloaded_since_last_request: int = 0

eggs_last_hour: int = 0
steps_last_hour: int = 0

purge_enabled: bool = False
purge_stage: int = 0
purge_start_unload: bool = False
purge_counter: int = 0
purge_all_timer = None

valve_delay: int = 200

model = "v5"

white_shade: int = 225

initialize_servo_flag = True


# ==================================================================================== #
#                                     Experiment 2                                     #
# ==================================================================================== #
def get_cage_number():
    cage_number = int(setup.CAGE_ID[-2:])
    return cage_number


def get_shift(cage_number: int):
    if cage_number == 1:
        return 0
    if cage_number == 2:
        return 1
    if cage_number == 3:
        return 2
    if cage_number == 4:
        return 3
    if cage_number == 5:
        return 4
    if cage_number == 6:
        return 0
    if cage_number == 7:
        return 1
    if cage_number == 8:
        return 2
    if cage_number == 9:
        return 3
    if cage_number == 10:
        return 4
    if cage_number == 11:
        return 0
    if cage_number == 12:
        return 1
    if cage_number == 13:
        return 2
    if cage_number == 14:
        return 3


# | AI | AI | AI | AI | PURGE |
# ============================= To be exposed if required ============================ #
experiment2_interval = 60
experiment2_purge_frequency = 5

# ====================================== Driven ====================================== #
experiment2_pot_counter = 0
experiment2_max_pot = 80
experiment2_sequence_number = 0
experiment2_previous_sequence_number = experiment2_purge_frequency + 1
experiment2_sequence_duration = 14 * experiment2_interval  # 14 min
# dummy out of bound value for initial toggling
cage_number = get_cage_number()
