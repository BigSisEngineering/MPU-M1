import threading
import logging
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

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


pnp_data_lock = threading.Lock()
pnp_data: PNPData = PNPData(
    0,
    True,
    False,
    pot_processed=0,
    egg_pot_detected=0,
    detection=False,
    number_of_egg_pot_since_last_ask=0,
    pnp_confidence=75
)

is_star_wheel_error: bool = False
is_unloader_error: bool = False

star_wheel_duration_ms: int = 600

dummy_enabled: bool = False
unload_probability: float = 1.0

pnp_enabled: bool = False
pnp_confidence: float = 0.75

MongoDB_INIT : bool = False

pot_processed: int = 0
pot_unloaded: int = 0
pot_unloaded_since_last_request: int = 0

purge_enabled: bool = False
purge_stage: int = 0
purge_start_unload: bool = False
purge_counter: int = 0

# logging
# logging.basicConfig(
#     filename="/home/linaro/SmartCage_4/Statistics.log",
#     level=logging.INFO,
#     format="%(asctime)s,%(message)s",
#     datefmt="%Y-%m-%d,%H:%M:%S",
# )
