import threading
from dataclasses import dataclass, asdict
import time
import logging
import datetime
import numpy as np

# ------------------------------------------------------------------------------------------------ #
from src.BscbAPI.BscbAPI import BScbAPI
from src.BscbAPI.BscbAPI import SensorID, Status
from src import CLI
from src.CLI import Level
from src import data, operation, comm, cloud
from src.tasks.camera import CAMERA

MongoDB_INIT = False
time_stamp = time.time()
sensor_timer_flag = False
sensor_time = None
sensor_timeout = 3600
fake_sw_init_counter = 0
timer_error = None


class StatusCode:
    SW_INITIALIZING = 0x00
    PRIMING_CHANNELS = 0x01
    UL_INITIALIZING = 0x02
    IDLE = 0x03
    ERROR_SW = 0x04
    ERROR_UL = 0x05


@dataclass
class BoardData:
    sensors_values: list
    star_wheel_status: str
    unloader_status: str
    mode: str
    status_code: int

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


def __update_status_code(status_code: StatusCode):
    global BOARD_DATA, lock
    with lock:
        BOARD_DATA.status_code = status_code


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


# ==================================================================================== #
#                                      Sub actions                                     #
# ==================================================================================== #
def __action_servo_initialize():
    global BOARD_DATA, BOARD, lock, KILLER

    with data.lock:
        data.initialize_servo_flag = False

    _auto_clear_error = 0

    while _auto_clear_error < data.max_auto_clear_error:
        __update_status_code(StatusCode.UL_INITIALIZING)
        ul_init_successful = BOARD.unloader_init()

        if ul_init_successful:  # if ul init successful, move on
            is_buffer_full: bool = False
            is_loader_get_pot: bool = False

            __update_status_code(StatusCode.PRIMING_CHANNELS)
            while not KILLER.is_set() and not is_buffer_full and not is_loader_get_pot:
                with lock:
                    BOARD_DATA.sensors_values = BOARD.ask_sensors()
                    is_buffer_full = BOARD.resolve_sensor_status(BOARD_DATA.sensors_values, SensorID.BUFFER.value) == 1
                    is_loader_get_pot = BOARD.resolve_sensor_status(BOARD_DATA.sensors_values, SensorID.LOAD.value) == 1

            __update_status_code(StatusCode.SW_INITIALIZING)
            sw_init_successful = BOARD.starWheel_init()
            if sw_init_successful:
                break
            else:
                __update_status_code(StatusCode.ERROR_SW)

        else:
            __update_status_code(StatusCode.ERROR_UL)

        _auto_clear_error += 1


# ==================================================================================== #
#                                      Main thread                                     #
# ==================================================================================== #
def update(stop_event: threading.Event):
    timer = time.time()
    while not stop_event.is_set():
        try:
            if time.time() - timer > (1 / 60):
                # read initialize flag
                with data.lock:
                    _initialize_servo_flag = data.initialize_servo_flag

                # perform 3 initialization attempts
                if _initialize_servo_flag:
                    __action_servo_initialize()

                # main loop
                execute()
                timer = time.time()
        except Exception as e:
            CLI.printline(Level.ERROR, f"(BscbAPI)-Loop error-{e}")


@comm.timer()
def execute():
    global BOARD_DATA, BOARD, lock, MongoDB_INIT, time_stamp, sensor_timer_flag, sensor_time, auto_clear_error, sensor_timeout, fake_sw_init_counter, timer_error
    try:
        # ===================================== Update board data ==================================== #
        with lock:
            BOARD_DATA.sensors_values = BOARD.ask_sensors()
            BOARD_DATA.star_wheel_status = get_str_from_Status(BOARD.star_wheel_status)
            BOARD_DATA.unloader_status = get_str_from_Status(BOARD.unloader_status)
            is_star_wheel_error = not BOARD.is_readback_status_normal(BOARD.star_wheel_status)
            is_unloader_error = not BOARD.is_readback_status_normal(BOARD.unloader_status)
            sensors_values = BOARD_DATA.sensors_values

            if sensor_timer_flag == False:
                sensor_time = None
            if sensors_values[0] < 100 or sensors_values[2] < 100:
                if sensor_timer_flag == False:
                    sensor_time = time.time()
                    sensor_timer_flag = True

        # ======================================= Check status ======================================= #
        CLI.printline(
            Level.INFO,
            f"SW status-{BOARD_DATA.star_wheel_status}, UL-{BOARD_DATA.unloader_status}",
        )

        # CLI.printline(
        #     Level.SPECIFIC,
        #     f"UL_POS-{BOARD.get_unloader_position()}",
        # )
        # time.sleep(0.05)

        # Check buffer
        is_buffer_full = BOARD.resolve_sensor_status(sensors_values, SensorID.BUFFER.value) == 1

        # Check loading slot
        is_loader_get_pot = BOARD.resolve_sensor_status(sensors_values, SensorID.LOAD.value) == 1

        is_safe_to_move = not is_star_wheel_error and not is_unloader_error and is_buffer_full and is_loader_get_pot
        # is_safe_to_move = True

        servos_ready = BOARD_DATA.star_wheel_status == "normal" and BOARD_DATA.unloader_status == "normal"

        if not is_safe_to_move:
            CLI.printline(
                Level.DEBUG,
                f"(background-loop) buffer>{is_buffer_full}-loader>{is_loader_get_pot}",
            )
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
            run_purge = data.purge_enabled
            run_experiment = data.experiment_enabled
            data.servos_ready = servos_ready
            # print(f'servos state {data.servos_ready}')
            # MongoDB_INIT = data.MongoDB_INIT
            run_purge = data.purge_enabled
            pnp_confidence = data.pnp_confidence
            cycle_time = data.pnp_data.cycle_time

        if is_star_wheel_error or is_unloader_error:
            logging.info(
                f"{'Starwheel overload' if is_star_wheel_error else 'Unloader overload'} at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            if auto_clear_error == 0:
                timer_error = time.time()
                print("timer for error set")
            BOARD.unloader_clear_error()
            time.sleep(0.1)
            BOARD.unloader_init()
            time.sleep(2)
            if get_str_from_Status(BOARD.unloader_status) == "normal" and IsUnloaderHomed():
                wait_until_buffer_and_loader_ready()
                BOARD.star_wheel_clear_error()
                time.sleep(0.1)
                # BOARD.starWheel_fake_init()
                BOARD.starWheel_init()
                is_star_wheel_error = not BOARD.is_readback_status_normal(BOARD.star_wheel_status)
                is_unloader_error = not BOARD.is_readback_status_normal(BOARD.unloader_status)
                is_safe_to_move = (
                    not is_star_wheel_error and not is_unloader_error and is_buffer_full and is_loader_get_pot
                )
                servos_ready = not is_star_wheel_error and not is_unloader_error
                if auto_clear_error >= data.max_auto_clear_error and (time.time() - timer_error) < 60:
                    with data.lock:
                        data.dummy_enabled = False
                        data.pnp_enabled = False
                        data.experiment_enabled = False
                auto_clear_error += 1
                print(f"auto clear error increased to  {auto_clear_error}")
            else:
                with data.lock:
                    data.dummy_enabled = False
                    data.pnp_enabled = False
                    data.experiment_enabled = False
                MongoDB_INIT == False
                auto_clear_error = 0
                print("auto_clear_error set to zero")
            print(f"camera ready : {CAMERA.device_ready}   and  servos ready :  {servos_ready}")

            if not CAMERA.device_ready or not servos_ready:
                BOARD.unloader_clear_error()
                time.sleep(0.5)
                BOARD.unloader_init()
                with data.lock:
                    data.pnp_enabled = False
                    data.experiment_enabled = False

        # ======================================= PNP? ======================================= #
        if run_pnp:
            if time.time() - time_stamp > cycle_time:
                time_stamp = time.time() if is_safe_to_move else time_stamp
                CLI.printline(Level.INFO, f"(Background)-Running PNP")
                with lock:
                    BOARD_DATA.mode = "pnp"
                if MongoDB_INIT == False:
                    cloud.DataBase = cloud.EggCounter()
                    MongoDB_INIT = True

                if sensor_timer_flag == True:
                    if sensor_time is not None:
                        sensor_timer = time.time() - sensor_time
                        print(f"sensors not triggered for {sensor_timer}")
                        if sensor_timer > sensor_timeout and sensors_values[0] > 100 and sensors_values[2] > 100:
                            CLI.printline(Level.INFO, f"sensors triggered again {sensors_values}")
                            cloud.DataBase = cloud.EggCounter()
                            sensor_timer_flag = False
                # print(f"mongo DB variable after : {MongoDB_INIT}")
                operation.pnp(BOARD, lock, is_safe_to_move, star_wheel_duration_ms, pnp_confidence)

            CLI.printline(Level.INFO, f"(Background)-PNP Waiting")
        # ====================================== Dummy? ====================================== #
        elif run_dummy:
            if time.time() - time_stamp > cycle_time:
                time_stamp = time.time() if is_safe_to_move else time_stamp
                with lock:
                    BOARD_DATA.mode = "dummy"
                CLI.printline(Level.INFO, f"(Background)-Running DUMMY")
                MongoDB_INIT == False
                # FIXME
                # operation.dummy(BOARD, lock, is_safe_to_move, star_wheel_duration_ms, unload_probability)
                operation.dummy(
                    BOARD,
                    lock,
                    is_safe_to_move,
                    star_wheel_duration_ms,
                    unload_probability,
                )
        # ======================================== Purge? ======================================== #
        elif run_purge:
            with lock:
                BOARD_DATA.mode = "purging"
            with data.lock:
                purge_stage = data.purge_stage
            CLI.printline(Level.INFO, f"(Background)-Running PURGING - {purge_stage}")
            operation.purge(BOARD, lock, data.purge_start_unload)

        # ======================================== Purge? ======================================== #
        elif run_experiment:
            if time.time() - time_stamp > cycle_time:
                time_stamp = time.time() if is_safe_to_move else time_stamp
                with lock:
                    BOARD_DATA.mode = "experiment"
                # MongoDB_INIT == False
                if MongoDB_INIT == False:
                    cloud.DataBase = cloud.EggCounter()
                    MongoDB_INIT = True

                if sensor_timer_flag == True:
                    print(f"variable sensor_time :{sensor_time}")
                    if sensor_time is not None:
                        sensor_timer = time.time() - sensor_time
                        print(f"sensors not triggered for {sensor_timer}")
                        if sensor_timer > sensor_timeout and sensors_values[0] > 100 and sensors_values[2] > 100:
                            CLI.printline(Level.INFO, f"sensors triggered again {sensors_values}")
                            cloud.DataBase = cloud.EggCounter()
                            sensor_timer_flag = False
                CLI.printline(Level.INFO, f"(Background)-Running EXPERIMENT ")
                operation.experiment(BOARD, lock, is_safe_to_move, star_wheel_duration_ms, pnp_confidence)

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
