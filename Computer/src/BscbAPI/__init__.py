import threading
from dataclasses import dataclass, asdict
import time

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
auto_clear_error = 0


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
    global BOARD_DATA, BOARD, lock, MongoDB_INIT, time_stamp, sensor_timer_flag, sensor_time, auto_clear_error
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
        CLI.printline(Level.INFO, f"SW status-{BOARD_DATA.star_wheel_status}, UL-{BOARD_DATA.unloader_status}")

        # Check buffer
        is_buffer_full = BOARD.resolve_sensor_status(sensors_values, SensorID.BUFFER.value) == 1

        # Check loading slot
        is_loader_get_pot = BOARD.resolve_sensor_status(sensors_values, SensorID.LOAD.value) == 1

        is_safe_to_move = not is_star_wheel_error and not is_unloader_error and is_buffer_full and is_loader_get_pot

        servos_ready = BOARD_DATA.star_wheel_status =='normal' and BOARD_DATA.unloader_status=='normal'

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
            run_purge = data.purge_enabled
            data.servos_ready = servos_ready
            print(f'servos state {data.servos_ready}')
            # MongoDB_INIT = data.MongoDB_INIT
            run_purge = data.purge_enabled
            pnp_confidence = data.pnp_confidence
            cycle_time = data.pnp_data.cycle_time
            if is_star_wheel_error or is_unloader_error or not servos_ready:
                if auto_clear_error < data.max_auto_clear_error:
                    CLI.printline(Level.WARNING, f'SW/UNLOADER Error detected -- Trying to Auto Initialize -- Attempt {auto_clear_error} ')
                    BOARD.unloader_init()
                    time.sleep(2)
                    BOARD.star_wheel_clear_error()
                    time.sleep(0.1)
                    BOARD.starWheel_init()
                    is_star_wheel_error = not BOARD.is_readback_status_normal(BOARD.star_wheel_status)
                    is_unloader_error = not BOARD.is_readback_status_normal(BOARD.unloader_status)
                    is_safe_to_move = not is_star_wheel_error and not is_unloader_error and is_buffer_full and is_loader_get_pot
                    auto_clear_error = 0 if is_safe_to_move else auto_clear_error + 1

                else:  
                    data.dummy_enabled = False
                    data.pnp_enabled = False
                    MongoDB_INIT == False
                    auto_clear_error = 0
                
            if not CAMERA.device_ready:
                data.pnp_enabled = False
                # print('PNP disabled please check camera connection ...')
                
        # ======================================= PNP? ======================================= #
        if run_pnp:
            if time.time() - time_stamp > cycle_time:
                    
                # is_safe_to_move = is_safe_to_move and CAMERA.device_ready  # move when both BOARD and CAMERA are ready
                time_stamp = time.time() if is_safe_to_move else time_stamp

                CLI.printline(Level.INFO, f"(Background)-Running PNP")
                with lock:
                    BOARD_DATA.mode = "pnp"
                # FIXME
                print(f"mongo DB variable before : {MongoDB_INIT}")
                if MongoDB_INIT == False:
                    cloud.DataBase = cloud.EggCounter()
                    MongoDB_INIT = True

                if sensor_timer_flag == True:
                    print(f"variable sensor_time :{sensor_time}")
                    if sensor_time is not None:
                        sensor_timer = time.time() - sensor_time
                        print(f"sensors not triggered for {sensor_timer}")
                        if sensor_timer > 20 and sensors_values[0] > 100 and sensors_values[2] > 100:
                            CLI.printline(Level.INFO, f"sensors triggered again {sensors_values}")
                            cloud.DataBase = cloud.EggCounter()
                            sensor_timer_flag = False
                print(f"mongo DB variable after : {MongoDB_INIT}")
                # operation.pnp(BOARD, lock, is_safe_to_move, star_wheel_duration_ms, pnp_confidence)
                operation.test_pnp(BOARD, lock, is_safe_to_move, star_wheel_duration_ms, pnp_confidence)

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
