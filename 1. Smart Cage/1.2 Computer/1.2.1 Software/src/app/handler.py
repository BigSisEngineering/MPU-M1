import threading
import streamlit as st

# ------------------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level
from src import data
from src import BscbAPI

# ################################################################################################ #
#                                             Functions                                            #
# ################################################################################################ #


def clear_star_wheel_error():
    thread = threading.Thread(target=_clear_star_wheel_error)
    thread.start()


def _clear_star_wheel_error():
    CLI.printline(Level.DEBUG, "(handler)-clear_star_wheel_error")
    with BscbAPI.lock:
        BscbAPI.BOARD.star_wheel_clear_error()
        data.is_star_wheel_error = False


# ------------------------------------------------------------------------------------------------ #
def init_star_wheel():
    with BscbAPI.lock:
        data: BscbAPI.Status = BscbAPI.BOARD.star_wheel_status
    if not BscbAPI.BOARD.is_readback_status_normal(data):
        return
    thread = threading.Thread(target=_init_star_wheel)
    thread.start()


def _init_star_wheel():
    CLI.printline(Level.DEBUG, "(handler)-_init_star_wheel")
    if BscbAPI.BOARD is not None:
        with BscbAPI.lock:
            BscbAPI.BOARD.starWheel_init()
        # sv.star_wheel_inited = True


# ------------------------------------------------------------------------------------------------ #
def enable_pnp():
    with BscbAPI.lock:
        data: BscbAPI.BoardData = BscbAPI.BOARD_DATA
    if data.mode == "idle" or data.mode == "pnp":
        thread = threading.Thread(target=_enable_pnp)
        thread.start()


def _enable_pnp():
    CLI.printline(Level.DEBUG, "(handler)-_enable_pnp")
    with data.lock:
        data.pnp_enabled = not data.pnp_enabled


# ------------------------------------------------------------------------------------------------ #
def init_unloader():
    with BscbAPI.lock:
        data: BscbAPI.Status = BscbAPI.BOARD.unloader_status
    if not BscbAPI.BOARD.is_readback_status_normal(data):
        return
    thread = threading.Thread(target=_init_unloader)
    thread.start()


def _init_unloader():
    CLI.printline(Level.DEBUG, "(handler)-_init_unloader")
    if BscbAPI.BOARD is not None:
        with BscbAPI.lock:
            BscbAPI.BOARD.unloader_init()
        # sv.unloader_inited = True


# ------------------------------------------------------------------------------------------------ #
def clear_unloader_error():
    thread = threading.Thread(target=_clear_unloader_error)
    thread.start()


def _clear_unloader_error():
    CLI.printline(Level.DEBUG, "(handler)-_clear_unloader_error")
    with BscbAPI.lock:
        BscbAPI.BOARD.unloader_clear_error()
    with data.lock:
        data.is_unloader_error = False


# ------------------------------------------------------------------------------------------------ #
def move_star_wheel_ccw():
    thread = threading.Thread(target=_move_star_wheel_ccw)
    thread.start()


def _move_star_wheel_ccw():
    CLI.printline(Level.DEBUG, "(handler)-_move_star_wheel_ccw")
    with BscbAPI.lock:
        BscbAPI.BOARD.star_wheel_move_back()


# ------------------------------------------------------------------------------------------------ #
def move_star_wheel_cw():
    thread = threading.Thread(target=_move_star_wheel_cw)
    thread.start()


def _move_star_wheel_cw():
    CLI.printline(Level.DEBUG, "(handler)-_move_star_wheel_cw")
    with data.lock:
        ms = data.star_wheel_duration_ms

    with BscbAPI.lock:
        BscbAPI.BOARD.star_wheel_move_ms(ms)


# ------------------------------------------------------------------------------------------------ #
def unload():
    thread = threading.Thread(target=_unload)
    thread.start()


def _unload():
    CLI.printline(Level.DEBUG, "(handler)-_unload")
    with BscbAPI.lock:
        BscbAPI.BOARD.unload()


# ------------------------------------------------------------------------------------------------ #
def enable_dummy():
    with BscbAPI.lock:
        res: BscbAPI.BoardData = BscbAPI.BOARD_DATA

    CLI.printline(Level.WARNING, f"(handler)-mode: {res.mode}")
    if res.mode == "idle" or res.mode == "dummy":
        thread = threading.Thread(target=_enable_dummy)
        thread.start()


def _enable_dummy():
    CLI.printline(Level.WARNING, "(handler)-_enable_dummy")
    with data.lock:
        data.dummy_enabled = not data.dummy_enabled


# ------------------------------------------------------------------------------------------------ #
