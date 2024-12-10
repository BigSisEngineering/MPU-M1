import threading
import json

from src.tasks import (
    a1_pot_sorter,
    a2_diet_dispenser,
    a3_pot_dispenser,
    c1_chimney_sorter,
    c2_chimney_placer,
    cage_score,
)

A1 = a1_pot_sorter.Task()
A2 = a2_diet_dispenser.Task()
A3 = a3_pot_dispenser.Task()
C1 = c1_chimney_sorter.Task()
C2 = c2_chimney_placer.Task()
CAGE_SCORE = cage_score.Task()


def _init():
    A1.start()
    A2.start()
    A3.start()
    C1.start()
    C2.start()
    CAGE_SCORE.start()


def start():
    threading.Thread(target=_init).start()


def generate_m1a_dict(raw_dict: bool = False):
    status_dict = {}

    status_dict["a1"] = A1.status
    status_dict["a2"] = A2.status
    status_dict["a3"] = A3.status

    if raw_dict:
        return status_dict

    return json.dumps(status_dict).encode()


def generate_m1c_dict(raw_dict: bool = False):
    status_dict = {}
    status_dict["c1"] = C1.status
    status_dict["c2"] = C2.status

    if raw_dict:
        return status_dict
    return json.dumps(status_dict).encode()
