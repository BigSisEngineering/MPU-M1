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
# experiment
def get_start_delay():
    global experiment2_time_per_sequence
    cage_number = int(setup.CAGE_ID[-2:])
    return (cage_number - 1) * (experiment2_time_per_sequence / 14 / 60) * 60


# | AI | AI | AI | AI | PURGE |
# ============================= To be exposed if required ============================ #
experiment2_current_iteration = 0  # set from master
experiment2_max_iteration = 5
experiment2_time_per_sequence = 14 * 60  # 14 min

# ====================================== Driven ====================================== #
experiment2_staggered_delay = get_start_delay()
experiment2_purge_iteration = experiment2_max_iteration - 1
experiment2_pot_counter = 0
experiment2_max_pot = 80
experiment2_time_stamp = None
experiment2_new_session = True

# logging
# logging.basicConfig(
#     filename="/home/linaro/SmartCage_4/Statistics.log",
#     level=logging.INFO,
#     format="%(asctime)s,%(message)s",
#     datefmt="%Y-%m-%d,%H:%M:%S",
# )
