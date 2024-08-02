# import json
# import random
# import time

# # ------------------------------------------------------------------------------------------------ #
# from src import data
# from src import BscbAPI
# from src import CLI
# from src.CLI import Level

# GET_LIST = ["ACK", "BoardData", "DummyData", "PNPData", "potData", "ERROR"]


# def send_200_response(server):
#     server.send_response(200)
#     server.send_header("Cache-Control", "no-cache, private")
#     server.send_header("Pragma", "no-cache")
#     server.send_header("Content-Type", "application/json")
#     server.end_headers()


# def generateFuncName(arg):
#     return f"get_{arg}"


# def get_ACK(server) -> None:
#     CLI.printline(Level.DEBUG, "(http_server)-get_ACK")
#     send_200_response(server)


# def get_BoardData(server):
#     CLI.printline(Level.DEBUG, "(http_server)-get_BoardData")
#     send_200_response(server)
#     with BscbAPI.lock:
#         # board_data = data.board_data.copy()
#         board_data = BscbAPI.BOARD_DATA
#     server.wfile.write(json.dumps(board_data.dict()).encode())


# def get_DummyData(server):
#     CLI.printline(Level.DEBUG, "(http_server)-DummyData")
#     send_200_response(server)
#     with data.lock:
#         res = {
#             "unload_probability": data.unload_probability,
#             "star_wheel_duration_ms": data.star_wheel_duration_ms,
#         }
#     server.wfile.write(json.dumps(res).encode())


# def get_PNPData(server):
#     CLI.printline(Level.DEBUG, "(http_server)-PNPData")
#     send_200_response(server)
#     with data.lock:
#         # pnp_data = data.pnp_data.copy()
#         pnp_data = data.pnp_data
#     server.wfile.write(json.dumps(pnp_data.dict()).encode())


# def get_potData(server):
#     CLI.printline(Level.DEBUG, "(http_server)-get_potData")
#     send_200_response(server)
#     with data.lock:
#         num_pot = data.pot_unloaded - data.pot_unloaded_since_last_request
#         data.pot_unloaded_since_last_request = data.pot_unloaded
#     server.wfile.write(json.dumps(num_pot).encode())


# def get_ERROR(server):
#     CLI.printline(Level.DEBUG, "(http_server)-get_ERROR")
#     send_200_response(server)
#     data = dict()
#     data["star_wheel_error"] = data.is_star_wheel_error
#     data["unloader_error"] = data.is_unloader_error
#     server.wfile.write(json.dumps(data).encode())


# ------------------------------------------------------------------------------------------------ #
from flask import Blueprint, jsonify, make_response
from src import data, BscbAPI, CLI
from src.CLI import Level

get_api = Blueprint('get_api', __name__)

def get_ACK():
    CLI.printline(Level.DEBUG, "(http_server)-get_ACK")
    return {}

def get_BoardData():
    CLI.printline(Level.DEBUG, "(http_server)-get_BoardData")
    with BscbAPI.lock:
        board_data = BscbAPI.BOARD_DATA.dict()
    return board_data

def get_DummyData():
    CLI.printline(Level.DEBUG, "(http_server)-DummyData")
    with data.lock:
        res = {
            "unload_probability": data.unload_probability,
            "star_wheel_duration_ms": data.star_wheel_duration_ms,
        }
    return res

def get_PNPData():
    CLI.printline(Level.DEBUG, "(http_server)-PNPData")
    with data.lock:
        pnp_data = data.pnp_data
    return pnp_data

def get_potData():
    CLI.printline(Level.DEBUG, "(http_server)-get_potData")
    with data.lock:
        num_pot = data.pot_unloaded - data.pot_unloaded_since_last_request
        data.pot_unloaded_since_last_request = data.pot_unloaded
    return num_pot

def get_ERROR():
    CLI.printline(Level.DEBUG, "(http_server)-get_ERROR")
    error_data = {
        "star_wheel_error": data.is_star_wheel_error,
        "unloader_error": data.is_unloader_error
    }
    return error_data

get_endpoints = {
    'ACK': get_ACK,
    'BoardData': get_BoardData,
    'DummyData': get_DummyData,
    'PNPData': get_PNPData,
    'potData': get_potData,
    'ERROR': get_ERROR
}

@get_api.route('/<endpoint>', methods=["GET"])
def handle_get(endpoint):
    if endpoint in get_endpoints:
        response_data = get_endpoints[endpoint]()
        response = make_response(jsonify(response_data), 200)
        return response
    else:
        return make_response(jsonify({"error": "Endpoint not found"}), 404)
