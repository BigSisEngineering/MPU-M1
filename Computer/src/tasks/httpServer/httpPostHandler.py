from flask import Blueprint, request, jsonify, make_response
import logging
import datetime
import time

# ------------------------------------------------------------------------------------------------ #
from src import BscbAPI
from src import data
from src import setup
from src.tasks import camera


post_api = Blueprint("post_api", __name__)


def __is_operation_running() -> bool:
    with data.lock:
        _dummy_enabled = data.dummy_enabled
        _pnp_enabled = data.pnp_enabled
        _experiment_enabled = data.experiment_enabled

    return _dummy_enabled or _pnp_enabled or _experiment_enabled


def post_star_wheel():
    # ? What is this for?
    # with BscbAPI("/dev/ttyACM0", 115200) as board:
    #     time_param = int(request.args.get("time", 0))
    #     board.starWheelInit()
    #     for _ in range(3):
    #         board.starWheelMoveTime(time_param)

    # ------------------------------------------------------------------------------------ #
    # !Rewritten code -> uses the correct 'BOARD' object
    time_param = int(request.args.get("time", 0))
    with BscbAPI.lock:
        BscbAPI.BOARD.star_wheel_init()

    for _ in range(3):
        with BscbAPI.lock:
            BscbAPI.BOARD.star_wheel_move_ms(time_param)

    return "Star Wheel operation completed"


def post_star_wheel_init():
    if not __is_operation_running():
        with BscbAPI.lock:
            outcome = BscbAPI.BOARD.star_wheel_init()
        return "SW init -> {}".format(outcome)
    return "Error, disable operation before proceeding"


def post_fake_star_wheel_init():
    if not __is_operation_running():
        with BscbAPI.lock:
            outcome = BscbAPI.BOARD.star_wheel_fake_init()
        return "SW fake init -> {}".format(outcome)
    return "Error, disable operation before proceeding"


def post_unloader_init():
    if not __is_operation_running():
        with BscbAPI.lock:
            outcome = BscbAPI.BOARD.unloader_init()
        return "SW fake init -> {}".format(outcome)
    return "Error, disable operation before proceeding"


def post_all_servos_init():
    with data.lock:
        # set flag to true, reset auto clear attempts
        data.initialize_servo_flag = True
        data.auto_clear_error_attempts = 0
    return "Initialize servo -> True"


def post_enable_dummy():
    with data.lock:
        data.dummy_enabled = True

    logging.info(f"Dummy mode enabled at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "Dummy enabled"


def post_enable_pnp():
    with data.lock:
        data.pnp_enabled = True

    logging.info(f"PNP mode enabled at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "PNP enabled"


def post_enable_experiment():  # defaults to 0 if start with cage UI
    with data.lock:
        data.experiment_enabled = True
        data.experiment2_pot_counter = 0
        data.experiment2_previous_sequence_number = -1  # reset to dummy value to trigger new index

    logging.info(f"Experiment mode enabled at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "Experiment enabled.".format()


def post_enable_purge():
    # !OBSOLETE
    with data.lock:
        data.purge_enabled = True

    logging.info(f"Purge mode enabled at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "Purge enabled"


def post_disable_dummy():
    with data.lock:
        data.dummy_enabled = False

    logging.info(f"Dummy mode disabled at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "Dummy disabled"


def post_disable_pnp():
    with data.lock:
        data.pnp_enabled = False

    logging.info(f"PNP mode disabled at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "PNP disabled"


def post_disable_experiment():
    with data.lock:
        data.experiment_status = ""
        data.experiment_enabled = False

    logging.info(f"Experiment mode disabled at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "Experiment mode disabled"


def post_set_star_wheel_speed(speed):
    # speed = int(speed)
    if 600 <= speed <= 5000:
        with data.lock:
            data.star_wheel_duration_ms = speed
        return f"Star wheel speed set to {speed}"
    return "Speed should be between 600-5000ms"


def post_set_dummy_unload_probability(probability):
    # probability = int(request.args.get('probability', 0))
    if 0 <= probability <= 100:
        with data.lock:
            data.unload_probability = probability / 100.0
        return f"Dummy unload probability set to {probability}%"
    return "Probability should be between 0-100"


def post_set_pnp_confidence_level(confidence):
    # confidence = int(request.args.get('confidence', 0))
    if 0 <= confidence <= 100:
        with data.lock:
            data.pnp_confidence = confidence / 100.0
        return f"PNP confidence level set to {confidence}%"
    return "Confidence should be between 0-100"


def post_clear_star_wheel_error():
    if not __is_operation_running():
        with BscbAPI.lock:
            outcome = BscbAPI.BOARD.star_wheel_clear_error()
        return "SW clear error -> {}".format(outcome)
    return "Error, disable operation before proceeding"


def post_clear_unloader_error():
    if not __is_operation_running():
        with BscbAPI.lock:
            outcome = BscbAPI.BOARD.unloader_clear_error()
        return "UL clear error -> {}".format(outcome)
    return "Error, disable operation before proceeding"


def post_clear_error():
    if not __is_operation_running():
        with BscbAPI.lock:
            outcome = BscbAPI.BOARD.star_wheel_clear_error() and BscbAPI.BOARD.unloader_clear_error()
        return "SW, UL clear error -> {}".format(outcome)
    return "Error, disable operation before proceeding"


def post_move_cw():
    if not __is_operation_running():
        with data.lock:
            ms = data.star_wheel_duration_ms

        with BscbAPI.lock:
            outcome = BscbAPI.BOARD.star_wheel_move_ms(ms)

        return "SW cw at {:^5} ms -> {}".format(ms, outcome)
    return "Error, disable operation before proceeding"


def post_move_ccw():
    if not __is_operation_running():
        with BscbAPI.lock:
            outcome = BscbAPI.BOARD.star_wheel_move_back()
        return "SW ccw -> {}".format(outcome)
    return "Error, disable operation before proceeding"


def post_unload():
    if not __is_operation_running():
        with BscbAPI.lock:
            outcome = BscbAPI.BOARD.unload()
        return "Unload -> {}".format(outcome)
    return "Error, disable operation before proceeding"


def post_set_cycle_time(cycle_time):
    if 0 <= cycle_time <= 20:
        with data.lock:
            data.pnp_data.cycle_time = cycle_time

        logging.info(
            f"Cycle Time set to {cycle_time} seconds at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return f"Cycle time set to {cycle_time} seconds"
    return "Cycle time should be between 0-20 seconds"


def post_set_pause_interval(pause_interval):
    with data.lock:
        data.experiment_pause_interval = pause_interval
    # logging.info(f"Pause Interval set to {pause_interval} seconds at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return f"pause interval set to {pause_interval} seconds"


def post_set_white_shade(value):
    with data.lock:
        data.white_shade = value
    return f"white shade set to {value}"


def post_save_mask_coordinates():
    mask_coordinates = (setup.CENTER_X, setup.CENTER_Y, setup.RADIUS)
    setup.save_mask_coordinates(mask_coordinates)
    return f"Circle coordinates saved {mask_coordinates}"


def post_save_star_wheel_zero():
    if not __is_operation_running():
        with BscbAPI.lock:
            BscbAPI.BOARD.star_wheel_save_offset(0)
            BscbAPI.BOARD.unloader_init()
            BscbAPI.BOARD.star_wheel_init()
        return "Star wheel zero position saved"
    return "Error, disable operation before proceeding"


def post_save_star_wheel_offset(offset):
    if not __is_operation_running():
        with BscbAPI.lock:
            BscbAPI.BOARD.star_wheel_save_offset(offset)
            BscbAPI.BOARD.unloader_init()
            BscbAPI.BOARD.star_wheel_init()

        return f"Star wheel offset saved at {offset}"
    return "Error, disable operation before proceeding"


def post_move_star_wheel(pos):
    if not __is_operation_running():
        with BscbAPI.lock:
            BscbAPI.BOARD.star_wheel_move_count(pos)
        return f"Star wheel moved to position {pos} (absolute)"
    return "Error, disable operation before proceeding"


def post_move_star_wheel_relative(pos):
    if not __is_operation_running():
        with BscbAPI.lock:
            BscbAPI.BOARD.star_wheel_move_count_relative(pos)
        return f"Star wheel moved to position {pos} (relative)"
    return "Error, disable operation before proceeding"


def post_set_valve_delay(delay):
    if not __is_operation_running():
        with BscbAPI.lock:
            BscbAPI.BOARD.set_valve_delay(delay)
        logging.info(f"valve Delay set to {delay} ms at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return f"Valve delay set to {delay}"


# Mapping endpoints to functions and their required argument count
post_endpoints = {
    "STAR_WHEEL": {"func": post_star_wheel, "arg_num": 0},
    "STAR_WHEEL_INIT": {"func": post_star_wheel_init, "arg_num": 0},
    "STAR_WHEEL_FAKE_INIT": {"func": post_fake_star_wheel_init, "arg_num": 0},
    "UNLOADER_INIT": {"func": post_unloader_init, "arg_num": 0},
    "ALL_SERVOS_INIT": {"func": post_all_servos_init, "arg_num": 0},
    "ENABLE_DUMMY": {"func": post_enable_dummy, "arg_num": 0},
    "ENABLE_PNP": {"func": post_enable_pnp, "arg_num": 0},
    "ENABLE_EXPERIMENT": {"func": post_enable_experiment, "arg_num": 0},
    "ENABLE_PURGE": {"func": post_enable_purge, "arg_num": 0},
    "DISABLE_DUMMY": {"func": post_disable_dummy, "arg_num": 0},
    "DISABLE_PNP": {"func": post_disable_pnp, "arg_num": 0},
    "DISABLE_EXPERIMENT": {"func": post_disable_experiment, "arg_num": 0},
    "CLEAR_STAR_WHEEL_ERROR": {"func": post_clear_star_wheel_error, "arg_num": 0},
    "CLEAR_UNLOADER_ERROR": {"func": post_clear_unloader_error, "arg_num": 0},
    "CLEAR_ERROR": {"func": post_clear_error, "arg_num": 0},
    "MOVE_CW": {"func": post_move_cw, "arg_num": 0},
    "MOVE_CCW": {"func": post_move_ccw, "arg_num": 0},
    "UNLOAD": {"func": post_unload, "arg_num": 0},
    "SAVE_STAR_WHEEL_ZERO": {"func": post_save_star_wheel_zero, "arg_num": 0},
    "SAVE_MASK": {"func": post_save_mask_coordinates, "arg_num": 0},
    # Endpoints that require arguments
    "SAVE_STAR_WHEEL_OFFSET": {"func": post_save_star_wheel_offset, "arg_num": 1},
    "SET_STAR_WHEEL_SPEED": {"func": post_set_star_wheel_speed, "arg_num": 1},
    "SET_DUMMY_UNLOAD_PROBABILITY": {"func": post_set_dummy_unload_probability, "arg_num": 1},
    "SET_PNP_CONFIDENCE_LEVEL": {"func": post_set_pnp_confidence_level, "arg_num": 1},
    "SET_CYCLE_TIME": {"func": post_set_cycle_time, "arg_num": 1},
    "SET_PAUSE_INTERVAL": {"func": post_set_pause_interval, "arg_num": 1},
    "MOVE_STAR_WHEEL": {"func": post_move_star_wheel, "arg_num": 1},
    "MOVE_STAR_WHEEL_REL": {"func": post_move_star_wheel_relative, "arg_num": 1},
    "WHITE_SHADE": {"func": post_set_white_shade, "arg_num": 1},
    "VALVE_DELAY": {"func": post_set_valve_delay, "arg_num": 1},
}


@post_api.route("/<string:endpoint>", methods=["POST"])
def run_func(endpoint: str):
    if endpoint in post_endpoints and post_endpoints[endpoint]["arg_num"] == 0:
        try:
            result = post_endpoints[endpoint]["func"]()
            return make_response(result, 200)
        except Exception as e:
            return make_response(f"Error: {str(e)}", 500)
    return make_response("Invalid endpoint or incorrect method usage.", 404)


@post_api.route("/<string:endpoint>/<int:v1>", methods=["POST"])
def run_func_1_arg(endpoint: str, v1):
    if endpoint in post_endpoints and post_endpoints[endpoint]["arg_num"] == 1:
        try:
            result = post_endpoints[endpoint]["func"](v1)
            return make_response(result, 200)
        except Exception as e:
            return make_response(f"Error: {str(e)}", 500)
    return make_response("Invalid endpoint or incorrect method usage.", 404)
