from typing import Optional, Dict
import json
import time
import threading
import os
from pathlib import Path
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

base_dir = Path(__file__).resolve().parent.parent
json_path = base_dir / 'http_server' / 'static' / 'js' / 'cage_status.json'

cage_dict: Optional[Dict[Cages, cages.Cage]] = {}

for cage in Cages:
    cage_dict[cage] = cages.Cage(cage)

def generate_status_dict():
    status_dict = {}
    dict_1B = {}
    
    for cage in Cages:
        dict_1B[cage.value] = cage_dict[cage].status_ui
        # dict_1B[cage] = cage_dict[cage].status_ui
    # print(dict_1B)
    # print('----------------------')
    status_dict["b"] = dict_1B
    status_dict["a1"] = A1.status_ui
    status_dict["a2"] = A2.status_ui
    status_dict["a3"] = A3.status_ui
    status_dict["c1"] = C1.status_ui
    status_dict["c2"] = C2.status_ui
    # with open('MasterApp\src\http_server\static\js\cage_status.json', 'w') as json_file:
    # with open('src\http_server\static\js\cage_status.json', 'w') as json_file:
    #     json.dump(status_dict, json_file,  indent=4)

    with json_path.open('w') as json_file:
        json.dump(status_dict, json_file, indent=4)
    
    return json.dumps(status_dict)
  

def _update_status():
    time_stamp = time.time()
    while not SV.KILLER_EVENT.is_set():
        if time.time() - time_stamp > SV.BG_WATCHDOG:
            time_stamp = time.time()
            generate_status_dict()


threading.Thread(target=_update_status).start()

