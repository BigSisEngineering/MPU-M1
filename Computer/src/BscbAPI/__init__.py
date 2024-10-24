import threading
from dataclasses import dataclass, asdict
import time
import logging
import datetime

# ------------------------------------------------------------------------------------------------ #
from src.BscbAPI.BscbAPI import BScbAPI
from src.BscbAPI.BscbAPI import SensorID, Status
from src import CLI
from src.CLI import Level
from src import data, operation, comm, cloud
from src.tasks.camera import CAMERA

MongoDB_INIT = False
sensor_timer_flag = False
sensor_time = None
sensor_timeout = 3600
make_auto_home_decision = False
update_error_timer = True
first_error = True
last_error = time.time()
time_stamp = time.time()


class StatusCode:
    SW_INITIALIZING = 0x00
    PRIMING_CHANNELS = 0x01
    UL_INITIALIZING = 0x02
    IDLE = 0x03
    ERROR_SW = 0x04
    ERROR_UL = 0x05
    CLEARING_SERVO_ERROR = 0x06
    UNABLE_TO_CLEAR_ERROR = 0x07
    ERROR_CAMERA = 0x08
    NORMAL = 0x09
    LOADING = 0x10
    WAIT_ACK = 0x11
    SELF_FIX_PENDING = 0x12
    WAITING_FOR_BUFFER = 0x13
    WAITING_FOR_PASSIVE_LOAD = 0x14


class Mode:
    IDLE = "idle"
    PNP = "pnp"
    EXPERIMENT = "experiment"
    DUMMY = "dummy"
    PURGING = "purging"


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


def __update_mode(mode: Mode):
    global BOARD_DATA, lock
    with lock:
        BOARD_DATA.mode = mode


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
def __action_servo_initialize() -> None:
    global BOARD_DATA, BOARD, lock, KILLER, auto_clear_error, make_auto_home_decision, update_error_timer

    with data.lock:
        data.initialize_servo_flag = False

    auto_clear_error = 0
    _ul_init_successful: bool = False
    _sw_init_successful: bool = False

    while auto_clear_error < data.max_auto_clear_error:
        # clear error
        __update_status_code(StatusCode.CLEARING_SERVO_ERROR)
        ul_error_cleared = BOARD.unloader_clear_error()
        sw_error_cleared = BOARD.star_wheel_clear_error()

        if ul_error_cleared and sw_error_cleared:
            # initialize unloader
            __update_status_code(StatusCode.UL_INITIALIZING)
            _ul_init_successful = BOARD.unloader_init()

            if _ul_init_successful:
                is_buffer_full: bool = False
                is_loader_get_pot: bool = False

                # wait for sensors to trigger (priming)
                __update_status_code(StatusCode.PRIMING_CHANNELS)
                while not KILLER.is_set() and not is_buffer_full and not is_loader_get_pot:
                    with lock:
                        BOARD_DATA.sensors_values = BOARD.ask_sensors()
                        is_buffer_full = (
                            BOARD.resolve_sensor_status(BOARD_DATA.sensors_values, SensorID.BUFFER.value) == 1
                        )
                        is_loader_get_pot = (
                            BOARD.resolve_sensor_status(BOARD_DATA.sensors_values, SensorID.LOAD.value) == 1
                        )

                # initialize sw
                __update_status_code(StatusCode.SW_INITIALIZING)
                _sw_init_successful = BOARD.starWheel_init()
                if _sw_init_successful:
                    break
                else:
                    __update_status_code(StatusCode.ERROR_SW)

            else:
                __update_status_code(StatusCode.ERROR_UL)
        else:
            __update_status_code(StatusCode.UNABLE_TO_CLEAR_ERROR)

        auto_clear_error += 1

    if _ul_init_successful and _sw_init_successful:
        # reset auto homing
        update_error_timer = True
        make_auto_home_decision = True
    else:
        # disable operation
        pass
        # ! temporarily never pass
        # __disable_operation()


def __disable_operation():
    with data.lock:
        data.dummy_enabled = False
        data.pnp_enabled = False
        data.experiment_enabled = False


def __disable_operation_with_camera():
    with data.lock:
        data.pnp_enabled = False
        data.experiment_enabled = False


# ==================================================================================== #
#                                      Main thread                                     #
# ==================================================================================== #
def update(stop_event: threading.Event):
    timer = time.time()
    while not stop_event.is_set():
        try:
            if time.time() - timer > (1 / 60):

                # main loop
                execute()

                # read initialize flag
                with data.lock:
                    _initialize_servo_flag = data.initialize_servo_flag

                # perform 3 initialization attempts
                if _initialize_servo_flag:
                    __action_servo_initialize()

                timer = time.time()
        except Exception as e:
            CLI.printline(Level.ERROR, f"(BscbAPI)-Loop error-{e}")


# ==================================================================================== #
#                                    Sub operations                                    #
# ==================================================================================== #
def __update_sensor_timer_flag(sensors_values) -> None:
    global sensor_timer_flag, sensor_time

    if sensor_timer_flag == False:
        sensor_time = None
    if sensors_values[SensorID.LOAD.value] < 100 or sensors_values[SensorID.BUFFER.value] < 100:
        if sensor_timer_flag == False:
            sensor_time = time.time()
            sensor_timer_flag = True


@comm.timer()
def execute():
    global BOARD_DATA, BOARD, lock, MongoDB_INIT, time_stamp, sensor_timer_flag, sensor_time, auto_clear_error, sensor_timeout, last_error, make_auto_home_decision, update_error_timer, first_error
    try:
        # ===================================== Update board data ==================================== #
        with lock:
            BOARD_DATA.sensors_values = BOARD.ask_sensors()
            BOARD_DATA.star_wheel_status = get_str_from_Status(BOARD.star_wheel_status)
            BOARD_DATA.unloader_status = get_str_from_Status(BOARD.unloader_status)
            is_star_wheel_error = not BOARD.is_readback_status_normal(BOARD.star_wheel_status)
            is_unloader_error = not BOARD.is_readback_status_normal(BOARD.unloader_status)
            is_star_wheel_ready = BOARD.is_servo_ready(BOARD.star_wheel_status)
            is_unloader_ready = BOARD.is_servo_ready(BOARD.unloader_status)
            sensors_values = BOARD_DATA.sensors_values

        __update_sensor_timer_flag(sensors_values)

        # ======================================= Check status ======================================= #
        # Check buffer
        is_buffer_full = BOARD.resolve_sensor_status(sensors_values, SensorID.BUFFER.value) == 1

        # Check loading slot
        is_loader_get_pot = BOARD.resolve_sensor_status(sensors_values, SensorID.LOAD.value) == 1

        is_safe_to_move = is_star_wheel_ready and is_unloader_ready and is_buffer_full and is_loader_get_pot

        is_camera_ready = CAMERA.device_ready

        is_camera_operation_ready = is_camera_ready and is_safe_to_move

        # ===================================== Check user input ===================================== #
        with data.lock:
            star_wheel_duration_ms = data.star_wheel_duration_ms
            unload_probability = data.unload_probability
            run_dummy = data.dummy_enabled
            run_pnp = data.pnp_enabled
            run_purge = data.purge_enabled
            run_experiment = data.experiment_enabled
            data.servos_ready = is_star_wheel_ready and is_unloader_ready
            run_purge = data.purge_enabled
            pnp_confidence = data.pnp_confidence
            cycle_time = data.pnp_data.cycle_time

        # ================================= Servo error check ================================ #
        if is_star_wheel_error or is_unloader_error:
            if make_auto_home_decision:  # used as flag
                make_auto_home_decision = False

                # initialize again if last error happened more than 60 seconds ago
                if first_error or (time.time() - last_error > 60):
                    with data.lock:
                        data.initialize_servo_flag = True

                    __update_status_code(StatusCode.SELF_FIX_PENDING)

                    # permanently set first error to false
                    first_error = False
                else:
                    __update_status_code(StatusCode.WAIT_ACK)

            # initialize timer for last error
            if update_error_timer:
                # log instance
                logging.info(
                    f"{'Starwheel overload' if is_star_wheel_error else 'Unloader overload'} at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                last_error = time.time()
                update_error_timer = False

        # =============================== System status update =============================== #
        if is_star_wheel_ready and is_unloader_ready:
            if not is_camera_ready:
                __update_status_code(StatusCode.ERROR_CAMERA)
                __disable_operation_with_camera()
            elif not is_buffer_full:
                __update_status_code(StatusCode.WAITING_FOR_BUFFER)
            elif is_buffer_full and not is_loader_get_pot:
                __update_status_code(StatusCode.WAITING_FOR_PASSIVE_LOAD)
            else:
                __update_status_code(StatusCode.NORMAL)

        # ==================================== Time stamp ==================================== #
        time_now = time.time()
        _dt = time_now - time_stamp

        # ======================================= PNP? ======================================= #
        if run_pnp:
            if _dt > cycle_time and is_camera_operation_ready:
                time_stamp = time.time()

                CLI.printline(Level.INFO, f"(Background)-Running PNP")
                __update_mode(Mode.PNP)

                # init session
                if MongoDB_INIT == False:
                    cloud.DataBase = cloud.EggCounter()
                    MongoDB_INIT = True

                # mongoDB entry (new session on timeout)
                if sensor_timer_flag == True:
                    if sensor_time is not None:
                        sensor_timer = time.time() - sensor_time
                        if (
                            sensor_timer > sensor_timeout
                            and sensors_values[SensorID.BUFFER.value] > 100
                            and sensors_values[SensorID.LOAD.value] > 100
                        ):
                            cloud.DataBase = cloud.EggCounter()
                            sensor_timer_flag = False

                # run PNP
                operation.pnp(BOARD, lock, is_camera_operation_ready, star_wheel_duration_ms, pnp_confidence)

            CLI.printline(
                Level.DEBUG,
                (
                    f"(Background)-PNP Countdown ->{round(_dt, 2) - cycle_time}"
                    if is_camera_operation_ready
                    else "(Background)-PNP Waiting for system"
                ),
            )

        # ====================================== Dummy? ====================================== #
        elif run_dummy:
            if _dt > cycle_time and is_safe_to_move:
                time_stamp = time.time()

                CLI.printline(Level.INFO, f"(Background)-Running DUMMY")
                __update_mode(Mode.DUMMY)

                MongoDB_INIT == False

                # run DUMMY
                operation.dummy(
                    BOARD,
                    lock,
                    is_safe_to_move,
                    star_wheel_duration_ms,
                    unload_probability,
                )

            CLI.printline(
                Level.DEBUG,
                (
                    f"(Background)-DUMMY Countdown ->{round(_dt, 2) - cycle_time}"
                    if is_safe_to_move
                    else "(Background)-DUMMY Waiting for system"
                ),
            )

        # ======================================== Purge? ======================================== #
        elif run_purge and is_safe_to_move:
            # !OBSOLETE
            __update_mode(Mode.PURGING)

            # with data.lock:
            #     purge_stage = data.purge_stage

            # CLI.printline(Level.INFO, f"(Background)-Running PURGING - {purge_stage}")
            # operation.purge(BOARD, lock, data.purge_start_unload)

        # ================================== Experiment mode ================================= #
        elif run_experiment:
            if _dt > cycle_time and is_camera_operation_ready:
                time_stamp = time.time()

                CLI.printline(Level.INFO, f"(Background)-Running EXPERIMENT ")
                __update_mode(Mode.EXPERIMENT)

                if MongoDB_INIT == False:
                    cloud.DataBase = cloud.EggCounter()
                    MongoDB_INIT = True

                # mongoDB entry (new session on timeout)
                if sensor_timer_flag == True:
                    if sensor_time is not None:
                        sensor_timer = time.time() - sensor_time
                        if (
                            sensor_timer > sensor_timeout
                            and sensors_values[SensorID.BUFFER.value] > 100
                            and sensors_values[SensorID.LOAD.value] > 100
                        ):
                            cloud.DataBase = cloud.EggCounter()
                            sensor_timer_flag = False

                # run EXPERIMENT
                operation.experiment(BOARD, lock, is_safe_to_move, star_wheel_duration_ms, pnp_confidence)

            CLI.printline(
                Level.DEBUG,
                (
                    f"(Background)-EXPERIMENT Countdown ->{round(_dt, 2) - cycle_time}"
                    if is_camera_operation_ready
                    else "(Background)-EXPERIMENT Waiting for system"
                ),
            )

        # ========================================= IDLE ========================================= #
        else:
            __update_mode(Mode.IDLE)
            MongoDB_INIT = False

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
    Mode.IDLE,
    StatusCode.LOADING,
)
