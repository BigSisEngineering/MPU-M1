import random
import time
import threading
from typing import Dict
from datetime import datetime  # NOTE FOR TESTING ONLY

# ------------------------------------------------------------------------------------------------ #
from src import data, cloud, comm
from src.tasks import camera
from src.BscbAPI.BscbAPI import BScbAPI
from src import vision
from src import setup
from src import CLI
from src.CLI import Level


purge_state: int = 0
sw_thread: threading.Thread = None
unload_thread: threading.Thread = None
star_wheel_move_time: int = data.star_wheel_duration_ms
ai_result = 0
threads: Dict[str, threading.Thread] = {
    "sw": None,
    "ul": None,
    "ai": None,
    "comm": None,
}


def pnp(
    BOARD: BScbAPI, lock: threading.Lock, is_safe_to_move: bool, star_wheel_move_time: int, pnp_confidence: float
):
    global threads

    def wait_thread_to_finish(id: str):
        if threads[f"{id}"] is not None:
            if threads[f"{id}"].is_alive():
                threads[f"{id}"].join()
                CLI.printline(Level.WARNING, f"(PnP)-waited {id}")

    def get_ai_result(image, pnp_confidence):
        global ai_result
        ai_result = vision.PNP.is_egg_detected(image, pnp_confidence)
        CLI.printline(Level.INFO, f"(PnP)-ai done")

    def comm_thread(BOARD: BScbAPI, image, pnp_confidence, tmp_egg_pot_counter, timestamp_of_image):
        global ai_result
        if ai_result <= 0 and BOARD.timer.is_it_overtime():
            camera.CAMERA.save_raw_frame(image, 0, 0, timestamp_of_image)  # NOTE FOR TESTING ONLY
        else:
            camera.CAMERA.save_raw_frame(image, pnp_confidence, ai_result, timestamp_of_image)  # NOTE FOR TESTING ONLY
        with data.lock:
            data.pot_processed += 1
            data.pot_unloaded += tmp_egg_pot_counter

    def _move_sw(BOARD: BScbAPI, lock: threading.Lock, star_wheel_move_time):
        with lock:
            BOARD.star_wheel_move_ms(star_wheel_move_time)

    def _unload(BOARD: BScbAPI, lock: threading.Lock):
        with lock:
            BOARD.unload()

    try:
        # ====================================== Sense Check ===================================== #
        if BOARD is None:
            return
        if not is_safe_to_move:
            return
        # ======================================== Camera ======================================== #
        wait_thread_to_finish("sw")
        image = camera.CAMERA.get_frame()
        timestamp_of_image = datetime.now()
        CLI.printline(Level.INFO, f"(PnP)-image captured")

        # ======================================= sw thread ====================================== #
        wait_thread_to_finish("ul")
        threads["sw"] = threading.Thread(
            target=_move_sw,
            args=(
                BOARD,
                lock,
                star_wheel_move_time,
            ),
        )
        threads["sw"].start()
        CLI.printline(Level.INFO, f"(PnP)-sw moving")
        # ======================================= AI thread ====================================== #
        wait_thread_to_finish("ai")
        threads["ai"] = threading.Thread(
            target=get_ai_result,
            args=(
                image,
                pnp_confidence,
            ),
        )
        threads["ai"].start()
        CLI.printline(Level.INFO, f"(PnP)-ai started")
        # ======================================= ul thread ====================================== #
        wait_thread_to_finish("sw")
        wait_thread_to_finish("ai")
        tmp_egg_pot_counter = 1 if (ai_result > 0 or BOARD.timer.is_it_overtime()) else 0
        if tmp_egg_pot_counter > 0:
            BOARD.timer.update_slot()
            threads["ul"] = threading.Thread(
                target=_unload,
                args=(
                    BOARD,
                    lock,
                ),
            )
            threads["ul"].start()
        # ====================================== comm thread ===================================== #

        threads["comm"] = threading.Thread(
            target=comm_thread,
            args=(
                BOARD,
                image,
                pnp_confidence,
                tmp_egg_pot_counter,
                timestamp_of_image,
            ),
        )
        threads["comm"].start()
        cloud.DataBase.data_update("egg" if ai_result > 0 else "noegg")

        if BOARD.timer.is_it_overtime():
            cloud.DataBase.data_update("other")
        else:
            cloud.DataBase.data_update("egg" if ai_result > 0 else "noegg")

        cloud.DataBase.data_upload()
        BOARD.timer.move_index()

    except Exception as e:
        CLI.printline(Level.ERROR, f"(PnP)-{e}")




def dummy(
    BOARD: BScbAPI, lock: threading.Lock, is_safe_to_move: bool, star_wheel_duration_ms: int, unload_probability: float
):
    global threads

    def wait_thread_to_finish(id: str):
        if threads[f"{id}"] is not None:
            if threads[f"{id}"].is_alive():
                threads[f"{id}"].join()
                CLI.printline(Level.WARNING, f"(dummy)-waited {id}")

    def get_ai_result(unload_probability):
        global ai_result
        ai_result = random.random() < unload_probability
        # ai_result = (ai_result + 1) % 2
        time.sleep(0.9)
        CLI.printline(Level.INFO, f"(dummy)-fake ai done")

    def comm_thread(BOARD: BScbAPI, tmp_egg_pot_counter):
        with data.lock:
            data.pot_processed += 1
            data.pot_unloaded += tmp_egg_pot_counter

    def _move_sw(BOARD: BScbAPI, lock: threading.Lock, star_wheel_move_time):
        with lock:
            BOARD.star_wheel_move_ms(star_wheel_move_time)

    def _unload(BOARD: BScbAPI, lock: threading.Lock):
        with lock:
            BOARD.unload()

    try:
        # ====================================== Sense Check ===================================== #
        if BOARD is None:
            return
        if not is_safe_to_move:
            return
        # ======================================= sw thread ====================================== #
        wait_thread_to_finish("sw")
        wait_thread_to_finish("ul")
        threads["sw"] = threading.Thread(
            target=_move_sw,
            args=(
                BOARD,
                lock,
                star_wheel_move_time,
            ),
        )
        threads["sw"].start()
        CLI.printline(Level.INFO, f"(dummy)-sw moving")
        # ======================================= AI thread ====================================== #
        wait_thread_to_finish("ai")
        threads["ai"] = threading.Thread(
            target=get_ai_result,
            args=(unload_probability,),
        )
        threads["ai"].start()
        CLI.printline(Level.INFO, f"(dummy)-fake ai started")
        # ======================================= ul thread ====================================== #
        wait_thread_to_finish("sw")
        wait_thread_to_finish("ai")
        timer_unload = need_unload_in_interval(ai_result > 0)

        CLI.printline(Level.INFO, f"(dummy)-{timer_unload}/{ai_result}")
        tmp_egg_pot_counter = 1 if (ai_result > 0 or timer_unload) else 0
        # cloud.DataBase.data_update("egg" if ai_result > 0 else "noegg")
        # cloud.DataBase.data_upload()
        if tmp_egg_pot_counter > 0:
            threads["ul"] = threading.Thread(
                target=_unload,
                args=(
                    BOARD,
                    lock,
                ),
            )
            threads["ul"].start()
        # ====================================== comm thread ===================================== #

        threads["comm"] = threading.Thread(target=comm_thread, args=(BOARD, tmp_egg_pot_counter))
        threads["comm"].start()

    except Exception as e:
        CLI.printline(Level.ERROR, f"(PnP)-{e}")



def purge(BOARD: BScbAPI, lock: threading.Lock, is_filled: bool = False):
    # 1. The 1A will purge its old pot out
    if BOARD is not None:
        with data.lock:
            purge_state = data.purge_stage
        # 2. (RESET) the cage will unload pot(s) until the buffer sensor trigger
        if purge_state == 0:
            pass
            purge_state = 1
        # 3. (FILL) the 1A will send pots into cage system until the last cage auxiliary buffer sensor trigger
        #    around 160 pots
        # 4. (UNLOAD) Start to unload for 80+14 cycle and do the request as usual
        if purge_state == 1 and is_filled:
            with lock:
                BOARD.unload()
                BOARD.star_wheel_move_ms(600)
            with data.lock:
                data.pot_unloaded += 1
                data.purge_counter += 1
                if data.purge_counter >= 94:
                    purge_state = 2
                    data.pot_unloaded = 0
                    data.pot_unloaded_since_last_request = 0
        with data.lock:
            data.purge_stage = purge_state


timestamp: time.time = 0


def need_unload_in_interval(is_prev_unloaded: bool, interval_s: float = 5.0):
    global timestamp
    current = timestamp
    res = (time.time() - current) > interval_s
    if is_prev_unloaded or res:
        timestamp = time.time()
    return res