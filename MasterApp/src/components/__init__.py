from typing import Optional, Dict

# -------------------------------------------------------- #

from src._shared_variables import Cages, SV

# -------------------------------------------------------- #

from src.components import (
    a1_pot_sorter,
    a2_diet_dispenser,
    a3_pot_dispenser,
    c1_chimney_sorter,
    c2_chimney_placer,
    cages,
)

A1 = a1_pot_sorter.PotSorter()
A2 = a2_diet_dispenser.DietDispenser()
A3 = a3_pot_dispenser.PotDispenser()
C1 = c1_chimney_sorter.ChimneySorter()
C2 = c2_chimney_placer.ChimneyPlacer()

cage_dict: Optional[Dict[Cages, cages.Cage]] = {}

for cage in Cages:
    cage_dict[cage] = cages.Cage(cage)

# import json
# def generate_mega_dict_encoded():
#     dict = {}
#     dict_1B = {}
#     for cage in Cages:
#         dict_1B[cage.value] = cage_dict[cage].status_ui

#     dict["b"] = dict_1B
#     dict["a1"] = A1.status_ui
#     dict["a2"] = A2.status_ui
#     dict["a3"] = A3.status_ui
#     dict["c1"] = C2.status_ui
#     dict["c2"] = C2.status_ui

#     return json.dump(dict).encoded()
# # ------------------------------------------------------------------------------------ #
# def debug():
#     while not SV.KILLER_EVENT.is_set():
#         for cage in Cages:
#             print(f"{cage.value}: {cage_dict[cage].status_ui}\n")

#         # ------------------------------------------------------------------------------------ #
#         print(f"a1: {A1.status_ui}\n")
#         print(f"a2: {A2.status_ui}\n")
#         print(f"a3: {A3.status_ui}\n")
#         print(f"c1: {C1.status_ui}\n")
#         print(f"c2: {C2.status_ui}\n")


import json
import time
import os

def generate_mega_dict_encoded():
    mega_dict = {}
    dict_1B = {}
    
    for cage in Cages:
        dict_1B[cage.value] = cage_dict[cage].status_ui
    
    mega_dict["b"] = dict_1B
    mega_dict["a1"] = A1.status_ui
    mega_dict["a2"] = A2.status_ui
    mega_dict["a3"] = A3.status_ui
    mega_dict["c1"] = C1.status_ui
    mega_dict["c2"] = C2.status_ui

    with open('MasterApp/src/front_end/static/js/cage_status.json', 'w') as json_file:
        json.dump(mega_dict, json_file,  indent=4)
    
    return json.dumps(mega_dict)
  

def debug():
    while not SV.KILLER_EVENT.is_set():
        mega_dict_json = generate_mega_dict_encoded()
        time.sleep(3.5)

  
