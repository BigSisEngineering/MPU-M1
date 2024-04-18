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
    c3_channelizer,
    cages,
)

A1 = a1_pot_sorter.PotSorter()
A2 = a2_diet_dispenser.DietDispenser()
A3 = a3_pot_dispenser.PotDispenser()
C1 = c1_chimney_sorter.ChimneySorter()
C2 = c2_chimney_placer.ChimneyPlacer()
C3 = c3_channelizer.Channelizer()

cage_dict: Optional[Dict[Cages, cages.Cage]] = {}

for cage in Cages:
    cage_dict[cage] = cages.Cage(cage)


# -------------------------------------------------------- #
default_1A_status_dict = {
    "pot_sorter": {
        "connected": False,
        "running": False,
        "pot buffer status": False,
    },
    "diet_dispenser": {
        "connected": False,
        "running": False,
        "dispenser homed": False,
        "pot sensor status": False,
        "infeed buffer status": False,
        "outfeed buffer status": False,
    },
    "pot_dispenser": {
        "connected": False,
        "running": False,
        "pot buffer status": False,
        "pot sensor status": False,
    },
}


def get_1A_status() -> Dict:
    try:
        dict = {
            "pot_sorter": {
                "connected": A1.is_connected,
                "running": True if not A1.is_idle else False,
                "pot buffer status": (
                    True if A1.read_object("sensors.gpIn[0].value") == 1 else False
                ),
            },
            "diet_dispenser": {
                "connected": A2.is_connected,
                "running": True if A2.read_global("run") == 1 else False,
                "dispenser homed": (
                    True if A2.read_global("flag_dispenser_homed") == 1 else False
                ),
                "pot sensor status": (
                    True if A2.read_object("sensors.gpIn[3].value") == 1 else False
                ),
                "infeed buffer status": (
                    True if A2.read_object("sensors.gpIn[1].value") == 1 else False
                ),
                "outfeed buffer status": (
                    True if A2.read_object("sensors.gpIn[2].value") == 1 else False
                ),
            },
            "pot_dispenser": {
                "connected": A3.is_connected,
                "running": True if (A3.is_connected and SV.run_1a) else False,
                "pot buffer status": (
                    True if A3.read_object("sensors.gpIn[0].value") == 1 else False
                ),
                "pot sensor status": (
                    True if A3.read_object("sensors.gpIn[1].value") == 1 else False
                ),
            },
        }
        return dict
    except:
        return default_1A_status_dict
