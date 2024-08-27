import time
from flask import Blueprint, request, jsonify, make_response
import logging
import datetime
# ------------------------------------------------------------------------------------------------ #
from src import BscbAPI
from src import data
from src.BscbAPI.BscbAPI import BScbAPI
from src.app import handler
from src import setup


post_api = Blueprint('post_api', __name__)

def post_star_wheel():
    with BscbAPI("/dev/ttyACM0", 115200) as board:
        time_param = int(request.args.get('time', 0))
        board.starWheelInit()
        for _ in range(3):
            board.starWheelMoveTime(time_param)
    return  "Star Wheel operation completed"

def post_star_wheel_init():
    with data.lock:
        if not data.dummy_enabled or not data.pnp_enabled:
            handler.init_star_wheel()
            return "Star wheel init will proceed"
    return "Error, disable dummy or pnp before proceeding"

def post_unloader_init():
    with data.lock:
        if not data.dummy_enabled or not data.pnp_enabled:
            handler.init_unloader()
            return  "Unloader init will proceed"
    return "Error, disable dummy or pnp before proceeding"

def post_all_servos_init():
    with data.lock:
        if data.servos_ready:
            handler.init_unloader()
            handler.clear_star_wheel_error()
            handler.init_star_wheel()
            return "All servos initialized"
    return "Error, disable dummy or pnp before proceeding"

def post_enable_dummy():
    with data.lock:
        if data.servos_ready:
            data.dummy_enabled = True
            logging.info(f"Dummy mode enabled at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return "Dummy enabled"
    return "Initialize servos first"

def post_enable_pnp():
    with data.lock:
        if data.servos_ready:
            data.pnp_enabled = True
            logging.info(f"PNP mode enabled at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return "PNP enabled"
    return "Initialize servos first"

def post_enable_experiment():
    with data.lock:
        if data.servos_ready:
            data.experiment_enabled = True
            logging.info(f"Experiment mode enabled at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return "Experiment mode enabled"
    return "Initialize servos first"

def post_enable_purge():
    with data.lock:
        if data.servos_ready:
            data.purge_enabled = True
            return "Purge enabled"
    return "Initialize servos first"

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
        data.experiment_enabled = False
        logging.info(f"Experiment mode disabled at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "Experiment mode disabled"

def post_set_star_wheel_speed(speed):
    with data.lock:
        # speed = int(speed)
        if 600 <= speed <= 5000:
            data.star_wheel_duration_ms = speed
            return f"Star wheel speed set to {speed}"
    return "Speed should be between 600-5000ms"

def post_set_dummy_unload_probability(probability):
    with data.lock:
        # probability = int(request.args.get('probability', 0))
        if 0 <= probability <= 100:
            data.unload_probability = probability / 100.0
            return f"Dummy unload probability set to {probability}%"
    return "Probability should be between 0-100"

def post_set_pnp_confidence_level(confidence):
    with data.lock:
        # confidence = int(request.args.get('confidence', 0))
        if 0 <= confidence <= 100:
            data.pnp_confidence = confidence / 100.0
            return f"PNP confidence level set to {confidence}%"
    return "Confidence should be between 0-100"

def post_clear_star_wheel_error():
    handler.clear_star_wheel_error()
    return "Star wheel error cleared"

def post_clear_unloader_error():
    handler.clear_unloader_error()
    return "Unloader error cleared"

def post_move_cw():
    handler.move_star_wheel_cw()
    return "Moved clockwise"

def post_move_ccw():
    handler.move_star_wheel_ccw()
    return "Moved counter-clockwise"

def post_unload():
    handler.unload()
    return "Unloaded successfully"

def post_set_cycle_time(cycle_time):
    with data.lock:
        if 0 <= cycle_time <= 20:
            data.pnp_data.cycle_time = cycle_time
            return  f"Cycle time set to {cycle_time} seconds"
    return "Cycle time should be between 0-20 seconds"

def post_set_pause_interval(pause_interval):
    with data.lock:
        data.experiment_pause_interval = pause_interval
        return  f"pause interval set to {pause_interval} seconds"
 

def post_save_mask_coordinates():
    mask_coordinates = (
        setup.CENTER_X,
        setup.CENTER_Y,
        setup.RADIUS
    )
    setup.save_mask_coordinates(mask_coordinates)
    return f"Circle coordinates saved {mask_coordinates}"

def post_save_star_wheel_zero():
     with data.lock:
        if not data.dummy_enabled or data.pnp_enabled:
            handler.save_star_wheel_zero()
            time.sleep(1)
            BscbAPI.BOARD.unloader_init()
            time.sleep(1)
            BscbAPI.BOARD.starWheel_init()
            return "Star wheel zero position saved"

def post_save_star_wheel_offset(offset):
    with data.lock:
        if not data.dummy_enabled or data.pnp_enabled:
            offset = data.sw_pos
            handler.save_star_wheel_offset()
            time.sleep(1)
            BscbAPI.BOARD.unloader_init()
            time.sleep(1)
            BscbAPI.BOARD.starWheel_init()
            # handler.init_star_wheel()
            return f"Star wheel offset saved at {offset}"


def post_move_star_wheel(pos):
    with data.lock:
        if not data.dummy_enabled or data.pnp_enabled:
            data.sw_pos = pos
            handler.move_star_wheel_to_pos()
            return f"Star wheel moved to position {pos}"
        else:
            return "Dummy or PNP is enabled, preventing operation."



# Mapping endpoints to functions and their required argument count
post_endpoints = {
    "STAR_WHEEL": {"func": post_star_wheel, "arg_num": 0},
    "STAR_WHEEL_INIT": {"func": post_star_wheel_init, "arg_num": 0},
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
    "MOVE_STAR_WHEEL": {"func": post_move_star_wheel, "arg_num": 1}
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

