from typing import Dict, Callable, Union
from flask import Blueprint, make_response, request

# ------------------------------------------------------------------------------------ #
from src.CLI import Level
from src import CLI

# ------------------------------------------------------------------------------------ #
from src._shared_variables import SV
from src.components import A2, A3
from src import tasks

# ------------------------------------------------------------------------------------ #
from src.http_server.backend import Operation

blueprint = Blueprint("post_handler", __name__)

post_endpoints = {
    "operate_cage": {"func": Operation.manage_cage_actions, "arg_num": 0},
    "set_maintainence_flag": {"func": Operation.set_cage_maintainence_flag, "arg_num": 0},
    #
    "start_1a": {"func": lambda: SV.w_run_1a(True), "arg_num": 0},
    "stop_1a": {"func": lambda: SV.w_run_1a(False), "arg_num": 0},
    "add_pots": {"func": lambda: tasks.A3.add_pots(10), "arg_num": 0},
    "raise_nozzle": {"func": A2.raise_nozzle, "arg_num": 0},
    "lower_nozzle": {"func": A2.reposition_nozzle, "arg_num": 0},
    "home_a2_sw": {"func": A2.sw_home, "arg_num": 0},
    "home_a3_sw": {"func": A3.sw_home, "arg_num": 0},
    "set_zero": {"func": tasks.A3.set_zero, "arg_num": 0},
    #
    "start_1c": {"func": lambda: SV.w_run_1c(True), "arg_num": 0},
    "stop_1c": {"func": lambda: SV.w_run_1c(False), "arg_num": 0},
}


@blueprint.route("/<string:endpoint>/", methods=["POST"])
def run_func_0(endpoint: str):
    if endpoint in post_endpoints and post_endpoints[endpoint]["arg_num"] == 0:

        data = request.get_json(silent=True)
        response = (
            make_response(post_endpoints[endpoint]["func"](), 200)
            if data is None
            else make_response(post_endpoints[endpoint]["func"](data), 200)
        )
    else:
        response = make_response("(POST) Invalid endpoint!", 404)
    return response
