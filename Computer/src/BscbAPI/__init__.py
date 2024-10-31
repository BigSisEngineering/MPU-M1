import threading
from dataclasses import dataclass, asdict
import time
import logging
import datetime
from typing import Optional

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

RAISE_FLAG_TIME = 5  # seconds
waiting_for_buffer_time_stamp: Optional[float] = None
waiting_for_passive_load_time_stamp: Optional[float] = None


class InitializeStep:
    CLEAR_ERROR = 0
    INIT_UNLOADER = 1
    WAIT_FOR_SENSORS = 2
    INIT_STARWHEEL = 3


initialize_step_current = InitializeStep.CLEAR_ERROR


class StatusCode:
    SW_INITIALIZING = 0
    PRIMING_CHANNELS = 1  # !obsolete
    UL_INITIALIZING = 2
    IDLE = 3
    ERROR_SW = 4
    ERROR_UL = 5
    CLEARING_SERVO_ERROR = 6
    UNABLE_TO_CLEAR_ERROR = 7
    ERROR_CAMERA = 8
    NORMAL = 9
    LOADING = 10
    WAIT_ACK = 11
    SELF_FIX_PENDING = 12
    WAITING_FOR_BUFFER = 13
    WAITING_FOR_PASSIVE_LOAD = 14
    INIT_WAITING_FOR_BUFFER = 15
    INIT_WAITING_FOR_PASSIVE_LOAD = 16


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
def __servo_initialize(is_buffer_full: bool, is_loader_get_pot: bool) -> None:
    global BOARD_DATA, BOARD, lock, KILLER, make_auto_home_decision, update_error_timer, initialize_step_current

    with data.lock:
        _auto_clear_attempts = data.auto_clear_error_attempts

    # ===================================== Give up? ===================================== #
    if _auto_clear_attempts >= data.max_auto_clear_error:
        # give up on auto init
        with data.lock:
            data.initialize_servo_flag = False

        # Require start from beginning
        initialize_step_current = InitializeStep.CLEAR_ERROR
        return

    # ====================================== Action ====================================== #
    if initialize_step_current == InitializeStep.CLEAR_ERROR:
        # clear error
        __update_status_code(StatusCode.CLEARING_SERVO_ERROR)
        _ul_error_cleared = BOARD.unloader_clear_error()
        _sw_error_cleared = BOARD.star_wheel_clear_error()

        if _ul_error_cleared and _sw_error_cleared:
            # move on to next step
            initialize_step_current = InitializeStep.INIT_UNLOADER
        else:
            # add to attempt on failure
            __update_status_code(StatusCode.UNABLE_TO_CLEAR_ERROR)
            with data.lock:
                data.auto_clear_error_attempts += 1
        return

    elif initialize_step_current == InitializeStep.INIT_UNLOADER:
        # init unloader
        __update_status_code(StatusCode.UL_INITIALIZING)
        _ul_init_successful = BOARD.unloader_init()

        if _ul_init_successful:
            # move on to next step
            initialize_step_current = InitializeStep.WAIT_FOR_SENSORS
        else:
            # add to attempt on failure
            __update_status_code(StatusCode.ERROR_UL)
            with data.lock:
                data.auto_clear_error_attempts += 1
        return

    elif initialize_step_current == InitializeStep.WAIT_FOR_SENSORS:
        if not is_buffer_full:
            # ?timestamp here as well
            __update_status_code(StatusCode.INIT_WAITING_FOR_BUFFER)

        elif is_buffer_full and not is_loader_get_pot:
            # ?timestamp here as well
            __update_status_code(StatusCode.INIT_WAITING_FOR_PASSIVE_LOAD)

        # wait
        elif is_buffer_full and is_loader_get_pot:
            # move on to next step
            initialize_step_current = InitializeStep.INIT_STARWHEEL
        return

    elif initialize_step_current == InitializeStep.INIT_STARWHEEL:
        # initialize sw
        __update_status_code(StatusCode.SW_INITIALIZING)
        _sw_init_successful = BOARD.star_wheel_init()

        if _sw_init_successful:
            # reset
            initialize_step_current = InitializeStep.CLEAR_ERROR
            update_error_timer = True
            make_auto_home_decision = True

            with data.lock:
                data.initialize_servo_flag = False
                data.auto_clear_error_attempts = 0
        else:
            # add to attempt on failure
            __update_status_code(StatusCode.ERROR_SW)
            with data.lock:
                data.auto_clear_error_attempts += 1
        return


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
    global BOARD_DATA, BOARD, lock, MongoDB_INIT, time_stamp, sensor_timer_flag, sensor_time, sensor_timeout
    global last_error, make_auto_home_decision, update_error_timer, first_error
    global RAISE_FLAG_TIME, waiting_for_buffer_time_stamp, waiting_for_passive_load_time_stamp

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

        # ==================================== Read status =================================== #
        # Check buffer
        is_buffer_full = BOARD.resolve_sensor_status(sensors_values, SensorID.BUFFER.value) == 1

        # Check loading slot
        is_loader_get_pot = BOARD.resolve_sensor_status(sensors_values, SensorID.LOAD.value) == 1

        is_safe_to_move = is_star_wheel_ready and is_unloader_ready and is_buffer_full and is_loader_get_pot

        is_camera_ready = CAMERA.device_ready

        is_camera_operation_ready = is_camera_ready and is_safe_to_move

        # ================================== Read user input ================================= #
        with data.lock:
            star_wheel_duration_ms = data.star_wheel_duration_ms
            unload_probability = data.unload_probability
            run_dummy = data.dummy_enabled
            run_pnp = data.pnp_enabled
            run_purge = data.purge_enabled
            run_experiment = data.experiment_enabled
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

                    logging.info(f"Auto fix requested at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    __update_status_code(StatusCode.SELF_FIX_PENDING)

                    # permanently set first error to false
                    first_error = False
                else:
                    logging.info(f"Too many errors raised at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    __update_status_code(StatusCode.WAIT_ACK)

            # initialize timer for last error
            if update_error_timer:
                # log instance
                if is_star_wheel_error:
                    logging.info(f"Starwheel overload at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                if is_unloader_error:
                    logging.info(f"Unloader overload at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                last_error = time.time()
                update_error_timer = False

        # =============================== System status update =============================== #
        if is_star_wheel_ready and is_unloader_ready:
            if not is_camera_ready:
                __update_status_code(StatusCode.ERROR_CAMERA)

            elif not is_buffer_full:
                # Initialize time stamp
                if waiting_for_buffer_time_stamp is None:
                    waiting_for_buffer_time_stamp = time.time()
                else:
                    # Raise flag (action: add pots / check flip at infeed / check sensor)
                    if time.time() - waiting_for_buffer_time_stamp >= RAISE_FLAG_TIME:
                        __update_status_code(StatusCode.WAITING_FOR_BUFFER)

            elif is_buffer_full and not is_loader_get_pot:
                # Initialize time stamp
                if waiting_for_passive_load_time_stamp is None:
                    waiting_for_passive_load_time_stamp = time.time()
                else:
                    # Raise flag (action: poke)
                    if time.time() - waiting_for_passive_load_time_stamp >= RAISE_FLAG_TIME:
                        __update_status_code(StatusCode.WAITING_FOR_PASSIVE_LOAD)

            else:
                # clear both time stamps on normal
                waiting_for_buffer_time_stamp = None
                waiting_for_passive_load_time_stamp = None
                __update_status_code(StatusCode.NORMAL)

        # ==================================== Time stamp ==================================== #
        time_now = time.time()
        _dt = time_now - time_stamp

        # ======================================= PNP? ======================================= #
        if run_pnp:
            __update_mode(Mode.PNP)
            _execute = _dt > cycle_time and is_camera_operation_ready

            if _execute:
                # only update timestamp if execute, else flush
                time_stamp = time.time()

                CLI.printline(Level.INFO, f"(Background)-Running PNP")

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

            else:
                CLI.printline(
                    Level.DEBUG,
                    (
                        f"(Background)-PNP Countdown ->{round(_dt, 2) - cycle_time}"
                        if is_camera_operation_ready
                        else "(Background)-PNP Waiting for system"
                    ),
                )

            # run PNP
            operation.pnp(BOARD, lock, _execute, star_wheel_duration_ms, pnp_confidence)

        # ====================================== Dummy? ====================================== #
        elif run_dummy:
            __update_mode(Mode.DUMMY)
            _execute = _dt > cycle_time and is_safe_to_move

            if _execute:
                time_stamp = time.time()

                CLI.printline(Level.INFO, f"(Background)-Running DUMMY")

                MongoDB_INIT == False

            else:
                CLI.printline(
                    Level.DEBUG,
                    (
                        f"(Background)-DUMMY Countdown ->{round(_dt, 2) - cycle_time}"
                        if is_safe_to_move
                        else "(Background)-DUMMY Waiting for system"
                    ),
                )

            # run DUMMY
            operation.dummy(BOARD, lock, _execute, star_wheel_duration_ms, unload_probability)

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
            __update_mode(Mode.EXPERIMENT)
            _execute = _dt > cycle_time and is_camera_operation_ready

            if _execute:
                time_stamp = time.time()

                CLI.printline(Level.INFO, f"(Background)-Running EXPERIMENT ")

                if MongoDB_INIT == False:
                    cloud.DataBase = cloud.EggCounter()
                    MongoDB_INIT = True

                # mongoDB entry (new session on timeout)
                # ? Becomes not session based
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

            else:
                CLI.printline(
                    Level.DEBUG,
                    (
                        f"(Background)-EXPERIMENT Countdown ->{round(_dt, 2) - cycle_time}"
                        if is_camera_operation_ready
                        else "(Background)-EXPERIMENT Waiting for system"
                    ),
                )

            # run EXPERIMENT
            operation.experiment(BOARD, lock, _execute, star_wheel_duration_ms, pnp_confidence)

        # ========================================= IDLE ========================================= #
        else:
            __update_mode(Mode.IDLE)
            MongoDB_INIT = False

        # ==================================== Initialize? =================================== #
        with data.lock:
            _initialize_servo_flag = data.initialize_servo_flag

        # perform initialization
        if _initialize_servo_flag:
            __servo_initialize(is_buffer_full, is_loader_get_pot)

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
