import streamlit as st
from datetime import datetime
import ast
import threading
import time
from enum import Enum

from typing import Optional, Dict, List, Any

# ------------------------------------------------------------------------------------------------ #
from src import tasks, components
from src._shared_variables import (
    SV,
    Cages,
    Status,
    Mode,
    cage_mode_dict,
    cage_status_dict,
)

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "UI BACKEND"


class PlaceholderID(Enum):
    query_1a_pot_sorter = 0
    query_1a_diet_dispenser = 1
    query_1a_pot_dispenser = 2
    # -------------------------------------------------------- #
    query_1c_chimney_sorter = 3
    query_1c_chimney_placer = 4
    query_1c_channelizer = 5
    # -------------------------------------------------------- #
    status_cage_01 = 6
    status_cage_02 = 7
    status_cage_03 = 8
    status_cage_04 = 9
    status_cage_05 = 10
    status_cage_06 = 11
    status_cage_07 = 12
    status_cage_08 = 13
    status_cage_09 = 14
    status_cage_10 = 15
    status_cage_11 = 16
    status_cage_12 = 17
    status_cage_13 = 18
    status_cage_14 = 19
    status_cage_15 = 20
    # -------------------------------------------------------- #
    mode_cage_01 = 21
    mode_cage_02 = 22
    mode_cage_03 = 23
    mode_cage_04 = 24
    mode_cage_05 = 25
    mode_cage_06 = 26
    mode_cage_07 = 27
    mode_cage_08 = 28
    mode_cage_09 = 29
    mode_cage_10 = 30
    mode_cage_11 = 31
    mode_cage_12 = 32
    mode_cage_13 = 33
    mode_cage_14 = 34
    mode_cage_15 = 35


for id in PlaceholderID:
    print(id)


def get_mode_emoji(mode: Mode):
    if mode == Mode.pnp_mode:
        return "🟢"
    elif mode == Mode.dummy_mode:
        return "🔵"
    elif mode == Mode.idle:
        return "🟡"
    elif mode == Mode.offline:
        return "⚫"


def get_status_emoji(status: Status):
    if status == Status.normal:
        return "🟩"
    elif status == Status.slot_empty:
        return "🟨"
    elif status == Status.error:
        return "🟥"
    elif status == Status.offline:
        return "⬛"
    elif status == Status.not_init:
        return "🟦"



# example
# cage_status = components.cage_dict[Cages.CAGE01].status_ui

def get_request_for_board_data(cage: Cages):
    try:
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ #
        #                      this                      #
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ #
        response = components.cage_dict[cage].status_ui
        # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ #

        sensor_values = ast.literal_eval(response["sensors_values"])
        is_sensor_ok = (sensor_values[0] >= 100) and (sensor_values[2] >= 100)
        if (
            response["star_wheel_status"] == "overload"
            or response["unloader_status"] == "overload"
        ):
            cage_status_dict[cage] = Status.error
        elif (
            response["star_wheel_status"] == "not_init"
            or response["unloader_status"] == "not_init"
        ):
            cage_status_dict[cage] = Status.not_init
        elif not is_sensor_ok:
            cage_status_dict[cage] = Status.slot_empty
        elif (
            response["star_wheel_status"] == "idle"
            or response["star_wheel_status"] == "normal"
            or response["unloader_status"] == "idle"
            or response["unloader_status"] == "normal"
        ):
            cage_status_dict[cage] = Status.normal
        else:
            cage_status_dict[cage] = Status.offline

        mode = response["mode"]
        if mode == "idle":
            cage_mode_dict[cage] = Mode.idle
        elif mode == "pnp":
            cage_mode_dict[cage] = Mode.pnp_mode
        elif mode == "dummy":
            cage_mode_dict[cage] = Mode.dummy_mode
        else:
            cage_mode_dict[cage] = Mode.offline

    except Exception as e:
        cage_mode_dict[cage] = Mode.offline
        cage_status_dict[cage] = Status.offline


def get_a1_text(dict) -> str:
    if not dict["pot_sorter"]["connected"]:
        return "it's not connected"
    elif not dict["pot_sorter"]["running"]:
        return "it's not running"
    elif not dict["pot_sorter"]["pot buffer status"]:
        return "pot buffer is full"
    else:
        return "I don't know"


def get_a2_text(dict) -> str:
    if not dict["diet_dispenser"]["connected"]:
        return "it's not connected"
    elif not dict["diet_dispenser"]["running"]:
        return "it's not running"
    elif not dict["diet_dispenser"]["dispenser homed"]:
        return "nozzle is raised"
    elif dict["diet_dispenser"]["infeed buffer status"]:
        return "empty infeed buffer"
    elif not dict["diet_dispenser"]["outfeed buffer status"]:
        return "full outfeed buffer"
    else:
        return "I don't know"


def get_a3_text(dict) -> str:
    if not dict["pot_dispenser"]["connected"]:
        return "it's not connected"
    elif not dict["pot_dispenser"]["running"]:
        return "it's not running"
    elif dict["pot_dispenser"]["pot buffer status"]:
        return "pot buffer is empty"
    else:
        return "I don't know"


# -------------------------------------------------------- #
class Content:
    def __init__(self) -> None:
        self._content = {}
        self._lock_content = {}

        for id in PlaceholderID:
            self._content[id] = "loading..."
            self._lock_content[id] = threading.Lock()

        # -------------------------------------------------------- #
        threading.Thread(target=self._update_1a).start()
        threading.Thread(target=self._update_1c).start()
        threading.Thread(target=self._update_cage).start()

    def _w_content(self, id: PlaceholderID, w: Any) -> None:
        with self._lock_content[id]:
            self._content[id] = w

    # -------------------------------------------------------- #
    def _update_1a(self) -> None:
        CLI.printline(
            Level.INFO,
            "({:^10})-({:^8}) Start".format(print_name, "Update 1A"),
        )
        time_stamp = time.time()
        while not SV.KILLER_EVENT.is_set():
            if time.time() - time_stamp > SV.BG_WATCHDOG:

                dict = components.get_1A_status()
                CLI.printline(
                    Level.INFO,
                    "({:^10})-({:^8}) Fetch".format(print_name, "Update 1A"),
                )

                self._w_content(
                    PlaceholderID.query_1a_pot_sorter,
                    (
                        "Yes"
                        if (
                            dict["pot_sorter"]["connected"]
                            and dict["pot_sorter"]["running"]
                            and dict["pot_sorter"]["pot buffer status"]
                        )
                        else "No, because {}".format(get_a1_text(dict))
                    ),
                )
                self._w_content(
                    PlaceholderID.query_1a_diet_dispenser,
                    (
                        "Yes"
                        if (
                            dict["diet_dispenser"]["connected"]
                            and dict["diet_dispenser"]["running"]
                            and dict["diet_dispenser"]["dispenser homed"]
                            and not dict["diet_dispenser"]["infeed buffer status"]
                            and dict["diet_dispenser"]["outfeed buffer status"]
                        )
                        else "No, because {}".format(get_a2_text(dict))
                    ),
                )
                self._w_content(
                    PlaceholderID.query_1a_pot_dispenser,
                    (
                        "Yes if pots requested."
                        if (
                            dict["pot_dispenser"]["connected"]
                            and dict["pot_dispenser"]["running"]
                            and not dict["pot_dispenser"]["pot buffer status"]
                        )
                        else "No, because {}".format(get_a3_text(dict))
                    ),
                )

                time_stamp = time.time()

    # -------------------------------------------------------- #
    def _update_1c(self) -> None:
        CLI.printline(
            Level.INFO,
            "({:^10})-({:^8}) Start".format(print_name, "Update 1C"),
        )
        time_stamp = time.time()
        while not SV.KILLER_EVENT.is_set():
            if time.time() - time_stamp > SV.BG_WATCHDOG:
                CLI.printline(
                    Level.INFO,
                    "({:^10})-({:^8}) Fetch".format(print_name, "Update 1C"),
                )

                self._w_content(PlaceholderID.query_1c_chimney_sorter, "N/A")
                self._w_content(PlaceholderID.query_1c_chimney_placer, "N/A")
                self._w_content(PlaceholderID.query_1c_channelizer, "N/A")

                time_stamp = time.time()

    # -------------------------------------------------------- #
    def _update_cage(self) -> None:
        CLI.printline(
            Level.INFO,
            "({:^10})-({:^8}) Start".format(print_name, "Update Cage"),
        )
        time_stamp = time.time()
        while not SV.KILLER_EVENT.is_set():
            if time.time() - time_stamp > SV.BG_WATCHDOG:
                CLI.printline(
                    Level.INFO,
                    "({:^10})-({:^8}) Fetch".format(print_name, "Update Cage"),
                )

                threads: List[threading.Thread] = []

                for cage in Cages:
                    t = threading.Thread(
                        target=get_request_for_board_data,
                        args=(cage,),
                    )
                    threads.append(t)
                    t.daemon = True
                    t.start()

                for t in threads:
                    t.join()

                for cage in Cages:
                    cage_number = cage.name[-2:]
                    for id in PlaceholderID:
                        if "mode" in id.name and cage_number in id.name:
                            self._w_content(
                                id,
                                get_mode_emoji(cage_mode_dict[cage]),
                            )

                for cage in Cages:
                    cage_number = cage.name[-2:]
                    for id in PlaceholderID:
                        if "status" in id.name and cage_number in id.name:
                            self._w_content(
                                id,
                                get_status_emoji(cage_status_dict[cage]),
                            )
                time_stamp = time.time()

    # -------------------------------------------------------- #
    def r_content(self, id: PlaceholderID) -> Any:
        with self._lock_content[id]:
            r = self._content[id]
        return r


content = Content()
