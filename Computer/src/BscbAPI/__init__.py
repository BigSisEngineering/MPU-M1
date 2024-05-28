import threading
from dataclasses import dataclass, asdict
import time

# ------------------------------------------------------------------------------------------------ #
from src.BscbAPI.BscbAPI import BScbAPI
from src.BscbAPI.BscbAPI import SensorID, Status
from src import CLI
from src.CLI import Level
from src import data, operation, comm, cloud

MongoDB_INIT = False
time_stamp = time.time()


@dataclass
class BoardData:
    sensors_values: list
    star_wheel_status: str
    unloader_status: str
    mode: str

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


def get_str_from_Status(input: Status):
    if input == Status.overload:
        return "overload"
    elif input == Status.error:
        return "error"
    elif input == Status.timeout:
        return "timeout"
    elif input == Status.normal:
        return "normal"
    elif input == Status.idle:
        return "idle"
    elif input == Status.not_init:
        return "not_init"
    else:
        return ""


def update(stop_event: threading.Event):
    global BOARD_DATA, BOARD, lock
    timer = time.time()
    while not stop_event.is_set():
        try:
            if time.time() - timer > (1 / 60):
                execute()
                timer = time.time()
        except Exception as e:
            CLI.printline(Level.ERROR, f"(BscbAPI)-Loop error-{e}")


@comm.timer()
def execute():
    global BOARD_DATA, BOARD, lock, MongoDB_INIT
    try:
        # ===================================== Update board data ==================================== #
        with lock:
            BOARD_DATA.sensors_values = BOARD.ask_sensors()
            BOARD_DATA.star_wheel_status = get_str_from_Status(BOARD.star_wheel_status)
            BOARD_DATA.unloader_status = get_str_from_Status(BOARD.unloader_status)
            is_star_wheel_error = not BOARD.is_readback_status_normal(BOARD.star_wheel_status)
            is_unloader_error = not BOARD.is_readback_status_normal(BOARD.unloader_status)
            sensors_values = BOARD_DATA.sensors_values

        # ======================================= Check status ======================================= #
        # CLI.printline(Level.INFO, f"SW status-{BOARD.star_wheel_status}, UL-{BOARD.unloader_status}")

        # Check buffer
        is_buffer_full = BOARD.resolve_sensor_status(sensors_values, SensorID.BUFFER.value) == 1

        # Check loading slot
        is_loader_get_pot = BOARD.resolve_sensor_status(sensors_values, SensorID.LOAD.value) == 1

        is_safe_to_move = not is_star_wheel_error and not is_unloader_error and is_buffer_full and is_loader_get_pot

        if not is_safe_to_move:
            CLI.printline(Level.DEBUG, f"(background-loop) buffer>{is_buffer_full}-loader>{is_loader_get_pot}")
            CLI.printline(
                Level.DEBUG,
                f"(background-loop) swErr>{is_star_wheel_error}-ulErr>{is_unloader_error}",
            )
        # ===================================== Check user input ===================================== #
        with data.lock:
            star_wheel_duration_ms = data.star_wheel_duration_ms
            unload_probability = data.unload_probability
            run_dummy = data.dummy_enabled
            run_pnp = data.pnp_enabled
            # MongoDB_INIT = data.MongoDB_INIT
            run_purge = data.purge_enabled
            pnp_confidence = data.pnp_confidence
            cycle_time = data.pnp_data.cycle_time
            if is_star_wheel_error or is_unloader_error:
                data.dummy_enabled = False
                data.pnp_enabled = False
                MongoDB_INIT == False
        # ======================================= PNP? ======================================= #
        if run_pnp:
            if time.time() - time_stamp > cycle_time:
                time_stamp = time.time() if is_safe_to_move else time_stamp

                CLI.printline(Level.INFO, f"(Background)-Running PNP")
                with lock:
                    BOARD_DATA.mode = "pnp"
                # FIXME
                print(f"mongo DB variable before : {MongoDB_INIT}")
                if MongoDB_INIT == False:
                    cloud.DataBase = cloud.EggCounter()
                    MongoDB_INIT = True
                print(f"mongo DB variable after : {MongoDB_INIT}")
                # operation.pnp(BOARD, lock, is_safe_to_move, star_wheel_duration_ms, pnp_confidence)
                operation.test_pnp(BOARD, lock, is_safe_to_move, star_wheel_duration_ms, pnp_confidence)

            CLI.printline(Level.INFO, f"(Background)-PNP Waiting")
        # ====================================== Dummy? ====================================== #
        elif run_dummy:
            with lock:
                BOARD_DATA.mode = "dummy"
            CLI.printline(Level.INFO, f"(Background)-Running DUMMY")
            MongoDB_INIT == False
            # FIXME
            # operation.dummy(BOARD, lock, is_safe_to_move, star_wheel_duration_ms, unload_probability)
            operation.test_dummy(BOARD, lock, is_safe_to_move, star_wheel_duration_ms, unload_probability)
        # ======================================== Purge? ======================================== #
        elif run_purge:
            with lock:
                BOARD_DATA.mode = "purging"
            with data.lock:
                purge_stage = data.purge_stage
            CLI.printline(Level.INFO, f"(Background)-Running PURGING - {purge_stage}")
            operation.purge(BOARD, lock, data.purge_start_unload)
        # ========================================= IDLE ========================================= #
        else:
            with lock:
                BOARD_DATA.mode = "idle"
            MongoDB_INIT = False
            CLI.printline(Level.INFO, f"(Background)-Running NOTHING")
    except Exception as e:
        CLI.printline(Level.ERROR, f"(BscbAPI)-Loop error-{e}")


def create_thread():
    global KILLER
    bg_thread = threading.Thread(target=update, args=(KILLER,))
    bg_thread.daemon = True
    return bg_thread


KILLER = threading.Event()
lock = threading.Lock()
BOARD = BScbAPI(baud_rate=115200)
BOARD_DATA = BoardData(
    [0, 0, 0, 0],
    "",
    "",
    "idle",
)
