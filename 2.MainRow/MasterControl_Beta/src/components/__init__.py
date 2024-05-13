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


# endpoints required for 1A
# /A2ClearSWError
# /A2ClearSWHome
# /A3ClearSWError
# /A3ClearSWHome

# -------------------------------------------------------- #
default_1A_status_dict = {
    "pot_sorter": {
        "connected": False,
        "running": False,
        "buff_out": False, # ! if False, the belt will not run
    },
    "diet_dispenser": {
        "connected": False,
        "running": False,
        "dispenser_homed": False, # ! need endpoint /lowerNozzle -> to reposition nozzle after auto nozzle raise for cleaning
        "sw_error": False, # ! if True , sw won't move (not implemented yet)
        "buff_in": False, # ! if True, sw won't move
        "buff_out": False, # ! if False, sw won't move
        "pot_sensor": False, # ! if dispensing misses
    },
    "pot_dispenser": {
        "connected": False,
        "running": False,
        "sw_error": False, # ! if True , sw won't move (not implemented yet)
        "buff_in": False, # ! if True, sw won't move
        "pot_sensor": False,
    },
}

default_1C_status_dict = {
    "chimney_sorter": {
        "connected": False,
        "running": False,
        "buff_out": False, # ! if True, nothing will run
        "chn1_sensor": False, # !if False, the channel itself won't run
        "chn2_sensor": False,
        "chn3_sensor": False,
    },
    "chimney_placer": {
        "connected": False,
        "running": False,
        "pot_sensor": False, # !if either pot or chimney is False, won't run
        "chimney_sensor": False,
    },
}


def get_1A_status() -> Dict:
    try:
        dict = {
            "pot_sorter": {
                "connected": A1.is_connected,
                "running": True if not A1.is_idle else False,
                "buff_out": True if A1.read_object("sensors.gpIn[0].value") == 1 else False,
            },
            "diet_dispenser": {
                "connected": A2.is_connected,
                "running": True if A2.read_global("run") == 1 else False,
                "dispenser_homed": True if A2.read_global("flag_dispenser_homed") == 1 else False,
                "pot_sensor": True if A2.read_object("sensors.gpIn[3].value") == 1 else False,
                "buff_in": True if A2.read_object("sensors.gpIn[1].value") == 1 else False,
                "buff_out": True if A2.read_object("sensors.gpIn[2].value") == 1 else False,
                "sw_error": False, # not implemented yet
            },
            "pot_dispenser": {
                "connected": A3.is_connected,
                "running": True if (A3.is_connected and SV.run_1a) else False,
                "buff_in": True if A3.read_object("sensors.gpIn[0].value") == 1 else False,
                "pot_sensor": True if A3.read_object("sensors.gpIn[1].value") == 1 else False,
                "sw_error": False, # not implemented yet
            },
        }
        return dict
    except:
        return default_1A_status_dict
    
def get_1C_status() -> Dict:
    try:
        dict = {
                "chimney_sorter": {
                    "connected": C1.is_connected,
                    "running": True if not C1.is_idle else False,
                    "chn1_sensor": True if C1.read_object("sensors.gpIn[0].value") == 1 else False,
                    "chn2_sensor": True if C1.read_object("sensors.gpIn[1].value") == 1 else False,
                    "chn3_sensor": True if C1.read_object("sensors.gpIn[2].value") == 1 else False,
                    "buff_out": True if C1.read_object("sensors.gpIn[3].value") == 1 else False,
                },
                "chimney_placer": {
                    "connected": C2.is_connected,
                    "running": True if not C2.is_idle else False,
                    "pot_sensor": True if C2.read_object("sensors.gpIn[1].value") == 1 else False,
                    "chimney_sensor": True if C2.read_object("sensors.gpIn[0].value") == 1 else False,
                },
            }
        return dict
    except:
        return default_1C_status_dict
