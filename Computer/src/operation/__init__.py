import random
import time
import threading
from typing import Dict
from datetime import datetime  # NOTE FOR TESTING ONLY
import logging

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
    is_it_overtime = BOARD.timer.is_it_overtime()

    def wait_thread_to_finish(id: str):
        if threads[f"{id}"] is not None:
            if threads[f"{id}"].is_alive():
                threads[f"{id}"].join()
                CLI.printline(Level.WARNING, f"(PnP)-waited {id}")

    def get_ai_result(image, pnp_confidence):
        global ai_result
        print(f'ai results: {ai_result}')
        ai_result = vision.PNP.is_egg_detected(image, pnp_confidence)
        CLI.printline(Level.INFO, f"(PnP)-ai done")

    def comm_thread(BOARD: BScbAPI, image, pnp_confidence, tmp_egg_pot_counter, timestamp_of_image):
        global ai_result
        if ai_result <= 0 and is_it_overtime:
            camera.CAMERA.save_raw_frame(image, 0, 0, timestamp_of_image)
        else:
            camera.CAMERA.save_raw_frame(image, pnp_confidence, ai_result, timestamp_of_image)
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
        tmp_egg_pot_counter = 1 if (ai_result > 0 or is_it_overtime) else 0
        if tmp_egg_pot_counter > 0:
            if data.model != 'v10': BOARD.timer.update_slot()
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
       
        if is_it_overtime:
            cloud.DataBase.data_update("other")
        else:
            cloud.DataBase.data_update("egg" if ai_result > 0 else "noegg")

        cloud.DataBase.data_upload()
        if data.model != 'v10': BOARD.timer.move_index()

    except Exception as e:
        CLI.printline(Level.ERROR, f"(PnP)-{e}")




def dummy(
    BOARD: BScbAPI, lock: threading.Lock, is_safe_to_move: bool, star_wheel_move_time: int, unload_probability: float
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
        logging.info(f"Dummy mode, pot unloaded at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        CLI.printline(Level.ERROR, f"(dummy)-{e}")



# def purge(BOARD: BScbAPI, lock: threading.Lock, is_filled: bool = False):
#     # 1. The 1A will purge its old pot out
#     if BOARD is not None:
#         with data.lock:
#             purge_state = data.purge_stage
#         # 2. (RESET) the cage will unload pot(s) until the buffer sensor trigger
#         if purge_state == 0:
#             pass
#             purge_state = 1
#         # 3. (FILL) the 1A will send pots into cage system until the last cage auxiliary buffer sensor trigger
#         #    around 160 pots
#         # 4. (UNLOAD) Start to unload for 80+14 cycle and do the request as usual
#         if purge_state == 1 and is_filled:
#             with lock:
#                 BOARD.unload()
#                 BOARD.star_wheel_move_ms(600)
#             with data.lock:
#                 data.pot_unloaded += 1
#                 data.purge_counter += 1
#                 if data.purge_counter >= 94:
#                     purge_state = 2
#                     data.pot_unloaded = 0
#                     data.pot_unloaded_since_last_request = 0
#         with data.lock:
#             data.purge_stage = purge_state

def purge(BOARD: BScbAPI, lock: threading.Lock, is_filled: bool = False):
    # 1. The 1A will purge its old pot out
    if BOARD is not None:
        # with data.lock:
        #     purge_state = data.purge_stage
        # # 2. (RESET) the cage will unload pot(s) until the buffer sensor trigger
        # if purge_state == 0:
        #     pass
        #     purge_state = 1
        # 3. (FILL) the 1A will send pots into cage system until the last cage auxiliary buffer sensor trigger
        #    around 160 pots
        # 4. (UNLOAD) Start to unload for 80+14 cycle and do the request as usual
        # if purge_state == 1 and is_filled:
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
        # with data.lock:
        #     data.purge_stage = purge_state

def experiment(BOARD: BScbAPI, lock: threading.Lock, is_safe_to_move: bool, star_wheel_move_time: int, pnp_confidence: float):
    global threads
    # t0 = time.time()
    def wait_thread_to_finish(id: str):
        if threads[f"{id}"] is not None:
            if threads[f"{id}"].is_alive():
                threads[f"{id}"].join()
                CLI.printline(Level.WARNING, f"(experiment mode)-waited {id}")

    def get_ai_result(image, pnp_confidence):
        global ai_result
        ai_result = vision.PNP.is_egg_detected(image, pnp_confidence)
        CLI.printline(Level.INFO, f"(Experiment)-ai done")

    def comm_thread(BOARD: BScbAPI, image, tmp_egg_pot_counter, timestamp_of_image):
        global ai_result
        camera.CAMERA.save_raw_frame(image, 1, ai_result, timestamp_of_image)
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
        
        with data.lock:
            if data.purge_counter >= 80:
                watchdog = data.experiment_pause_interval
                print(f'experiment status {data.experiment_pause_state}')
                if data.experiment_pause_state == False:
                    data.experiment_pause_start_time = time.time()
                    print(f'experiment status {data.experiment_pause_state}')
                    # start_time = datetime.fromtimestamp(data.experiment_pause_state).strftime('%H:%M:%S')
                    data.experiment_pause_state = True
                    logging.info(f"Experiment mode in Pause State for {watchdog} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    # CLI.printline(Level.INFO, f"(experiment mode)- pause state started at : {start_time} ")
                elapsed_time = time.time() - data.experiment_pause_start_time
                CLI.printline(Level.INFO, f"(experiment mode)- pause state - remaining time : {watchdog - elapsed_time} ")
                data.experiment_status = f'pause state for {watchdog}s - remaining time : {watchdog - elapsed_time}s'
                if elapsed_time > watchdog:
                    data.purge_counter = 0
                    data.experiment_pause_state = False
            else:
                wait_thread_to_finish("sw")
                image = camera.CAMERA.get_frame()
                timestamp_of_image = datetime.now()
                CLI.printline(Level.INFO, f"(Experiment)-image captured")
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
                CLI.printline(Level.INFO, f"(experiment mode)-sw moving")
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
                # timer_unload = need_unload_in_interval(ai_result > 0)

                # CLI.printline(Level.INFO, f"(experiment mode)-{timer_unload}/{ai_result}")
                # tmp_egg_pot_counter = 1 #if (ai_result > 0 or timer_unload) else 0
                tmp_egg_pot_counter = 1 if (ai_result > 0 or (time.time() - data.purge_all_timer)>3600) else 0
                if (time.time() - data.purge_all_timer) > 3600 and data.purge_counter == 80:
                    data.purge_all_timer = time.time()
                    # print()
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

                # threads["comm"] = threading.Thread(target=comm_thread, args=(BOARD, tmp_egg_pot_counter))
                # threads["comm"].start()
                threads["comm"] = threading.Thread(
                    target=comm_thread,
                    args=(
                        BOARD,
                        image,
                        # pnp_confidence,
                        tmp_egg_pot_counter,
                        timestamp_of_image,
                    ),
                )
                threads["comm"].start()
                data.purge_counter += 1
                CLI.printline(Level.INFO, f"(experiment mode)- purging state - pots unloaded : {data.purge_counter} ")
                data.experiment_status = f'purging state - pots unloaded : {data.purge_counter}' 
                logging.info(f"Experiment mode in Purging State, pot unloaded :{data.purge_counter} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        CLI.printline(Level.ERROR, f"(experiment mode)-{e}")

timestamp: time.time = 0


def need_unload_in_interval(is_prev_unloaded: bool, interval_s: float = 5.0):
    global timestamp
    current = timestamp
    res = (time.time() - current) > interval_s
    if is_prev_unloaded or res:
        timestamp = time.time()
    return res