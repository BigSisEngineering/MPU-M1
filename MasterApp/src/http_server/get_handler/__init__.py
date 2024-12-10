from typing import Dict, Callable, Any
from flask import Blueprint, make_response

# ------------------------------------------------------------------------------------ #
from src.CLI import Level
from src import CLI

# ------------------------------------------------------------------------------------ #
from src import components, tasks

# ------------------------------------------------------------------------------------ #
from src._shared_variables import SV

# ------------------------------------------------------------------------------------ #
from src import setup

blueprint = Blueprint("get_handler", __name__)


def _get_status(component: str) -> Any:
    if component == "m1a":
        return tasks.generate_m1a_dict()
    elif component == "m1c":
        return components.generate_m1c_dict()
    elif component == "cages":
        return components.generate_cage_dict()
    elif component == "system":
        return SV.system_status
    elif component == "info":
        return setup.get_setup_info()
    elif component == "cage_score":
        return tasks.cage_score_task.get_cage_score()
    else:
        return "null"


get_endpoints: Dict[str, Callable] = {
    "get_status": _get_status,
}


#
import time


@blueprint.route("/<string:endpoint>/<v1>", methods=["GET"])
def run_func(endpoint: str, v1: str):
    if endpoint in get_endpoints:
        response = make_response(get_endpoints[endpoint](v1), 200)
    else:
        response = make_response("(GET) Invalid endpoint!", 404)
    return response
