from typing import Optional, Dict
import json

# ------------------------------------------------------------------------------------ #
from src._shared_variables import Cages, SV
from src.components import (
    a1_pot_sorter,
    a2_diet_dispenser,
    a3_pot_dispenser,
    c1_chimney_sorter,
    c2_chimney_placer,
    cages,
)

# ------------------------------------------------------------------------------------ #
# init object
A1 = a1_pot_sorter.PotSorter()
A2 = a2_diet_dispenser.DietDispenser()
A3 = a3_pot_dispenser.PotDispenser()
C1 = c1_chimney_sorter.ChimneySorter()
C2 = c2_chimney_placer.ChimneyPlacer()

cage_dict: Optional[Dict[Cages, cages.Cage]] = {}

for cage in Cages:
    cage_dict[cage] = cages.Cage(cage)


# ------------------------------------------------------------------------------------ #
def generate_m1a_dict(raw_dict: bool = False):
    status_dict = {}

    status_dict["a1"] = A1.status_ui
    status_dict["a2"] = A2.status_ui
    status_dict["a3"] = A3.status_ui

    if raw_dict:
        return status_dict
    return json.dumps(status_dict).encode()


def generate_m1c_dict(raw_dict: bool = False):
    status_dict = {}
    status_dict["c1"] = C1.status_ui
    status_dict["c2"] = C2.status_ui

    if raw_dict:
        return status_dict
    return json.dumps(status_dict).encode()


def generate_cage_dict(raw_dict: bool = False):
    dict_1B = {}

    for cage in Cages:
        _dict = cage_dict[cage].status_ui
        _dict["maintainence_flag"] = cage_dict[cage].maintainence_flag
        dict_1B[cage.value] = _dict

    if raw_dict:
        return dict_1B
    return json.dumps(dict_1B).encode()
