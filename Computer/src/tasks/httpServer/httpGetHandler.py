# ------------------------------------------------------------------------------------------------ #
from flask import Blueprint, jsonify, make_response
from src import data, BscbAPI, CLI
from src.CLI import Level

get_api = Blueprint("get_api", __name__)


def get_ACK():
    return {}


def get_BoardData():
    with BscbAPI.lock:
        board_data = BscbAPI.BOARD_DATA.dict()
    return board_data


def get_UnloaderPos():
    with BscbAPI.lock:
        unloader_pos = BscbAPI.BOARD.get_unloader_position()
    return unloader_pos


def get_DummyData():
    with data.lock:
        res = {
            "unload_probability": data.unload_probability,
            "star_wheel_duration_ms": data.star_wheel_duration_ms,
        }
    return res


def get_PNPData():
    with data.lock:
        pnp_data = data.pnp_data
    return pnp_data


def get_potData():
    with data.lock:
        num_pot = data.pot_unloaded - data.pot_unloaded_since_last_request
        data.pot_unloaded_since_last_request = data.pot_unloaded
    return num_pot


def get_ERROR():
    with data.lock:
        error_data = {"star_wheel_error": data.is_star_wheel_error, "unloader_error": data.is_unloader_error}
    return error_data


def get_experimentData():
    with data.lock:
        experiment_status = data.experiment_status
    return experiment_status


def get_HOMING():
    with data.lock:
        sw_homing = data.sw_homing
    return sw_homing


def get_experimentStatus():
    dict = {}
    with data.lock:
        dict["operation_index"] = int(data.index_ui)  # float -> int
        dict["slots"] = data.experiment2_pot_counter
        dict["max_slots"] = data.STARWHEEL_SLOTS
        dict["time_elapsed"] = data.time_elapsed
        dict["sequence_duration"] = data.sequence_duration
        dict["sequence_number"] = data.experiment2_previous_sequence_number
        dict["purge_frequency"] = data.purge_frequency

    return dict


def get_experimentSettings():
    dict = {}
    with data.lock:
        dict["experiment_pause_interval"] = data.experiment_pause_interval
        dict["experiment_purge_frequency"] = data.purge_frequency
        dict["cycle_time"] = data.pnp_data.cycle_time
        dict["valve_delay"] = data.valve_delay

    return dict


get_endpoints = {
    "ACK": get_ACK,
    "BoardData": get_BoardData,
    "DummyData": get_DummyData,
    "PNPData": get_PNPData,
    "potData": get_potData,
    "ERROR": get_ERROR,
    "HOMING": get_HOMING,
    "ExperimentData": get_experimentData,
    "UnloaderPos": get_UnloaderPos,
    "ExperimentStatus": get_experimentStatus,
    "ExperimentSettings": get_experimentSettings,
}


@get_api.route("/<endpoint>", methods=["GET"])
def handle_get(endpoint):
    if endpoint in get_endpoints:
        response_data = get_endpoints[endpoint]()
        response = make_response(jsonify(response_data), 200)
        return response
    else:
        return make_response(jsonify({"error": "Endpoint not found"}), 404)
