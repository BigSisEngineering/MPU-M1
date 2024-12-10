import threading
import json

from src.tasks import a1, a2, a3, c1, c2, cage_score

A1 = a1.Task()
A2 = a2.Task()
A3 = a3.Task()
c1_task = c1.C1()
c2_task = c2.C2()
cage_score_task = cage_score.CageScore()


def _init():
    A1.start()
    A2.start()
    A3.start()
    c1_task.start()
    c2_task.start()
    cage_score_task.start()


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
