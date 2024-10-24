import random
import time
import threading
from typing import Dict
from datetime import datetime  # NOTE FOR TESTING ONLY
import logging

# ------------------------------------------------------------------------------------------------ #
from src import data, cloud
from src.tasks import camera
from src.BscbAPI.BscbAPI import BScbAPI
from src import vision
from src import CLI
from src.CLI import Level
from src import setup


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
counter = 0


def pnp(BOARD: BScbAPI, lock: threading.Lock, is_safe_to_move: bool, star_wheel_move_time: int, pnp_confidence: float):
    global threads
    is_it_overtime = BOARD.timer.is_it_overtime()

    def wait_thread_to_finish(id: str):
        if threads[f"{id}"] is not None:
            if threads[f"{id}"].is_alive():
                threads[f"{id}"].join()
                CLI.printline(Level.WARNING, f"(PnP)-waited {id}")

    def get_ai_result(image, pnp_confidence):
        global ai_result
        ai_result = vision.PNP.is_egg_detected(image, pnp_confidence)
        CLI.printline(Level.INFO, f"(PnP)-ai done. Results: {ai_result}")

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
            # blocks execution if either servo isn't ready
            is_star_wheel_ready = BOARD.is_servo_ready(BOARD.star_wheel_status)
            is_unloader_ready = BOARD.is_servo_ready(BOARD.unloader_status)

            if is_star_wheel_ready and is_unloader_ready:
                BOARD.star_wheel_move_ms(star_wheel_move_time)

    def _unload(BOARD: BScbAPI, lock: threading.Lock):
        with lock:
            # blocks execution if either servo isn't ready
            is_star_wheel_ready = BOARD.is_servo_ready(BOARD.star_wheel_status)
            is_unloader_ready = BOARD.is_servo_ready(BOARD.unloader_status)

            if is_star_wheel_ready and is_unloader_ready:
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
        # tmp_egg_pot_counter = 0
        if tmp_egg_pot_counter > 0:
            if data.model != "v10":
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

        if is_it_overtime:
            cloud.DataBase.data_update("other")
        else:
            cloud.DataBase.data_update("egg" if ai_result > 0 else "noegg")

        cloud.DataBase.data_upload()
        if data.model != "v10":
            BOARD.timer.move_index()

    except Exception as e:
        CLI.printline(Level.ERROR, f"(PnP)-{e}")


def dummy(
    BOARD: BScbAPI, lock: threading.Lock, is_safe_to_move: bool, star_wheel_move_time: int, unload_probability: float
):
    global threads, counter

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
        # tmp_egg_pot_counter = 0
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
        counter += 1

    except Exception as e:
        CLI.printline(Level.ERROR, f"(dummy)-{e}")


# !OBSOLETE
def purge(BOARD: BScbAPI, lock: threading.Lock, is_filled: bool = False):
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
    pass


# ==================================================================================== #
#                                       ORIGINAL                                       #
# ==================================================================================== #
# def experiment(
#     BOARD: BScbAPI, lock: threading.Lock, is_safe_to_move: bool, star_wheel_move_time: int, pnp_confidence: float
# ):
#     global threads

#     def wait_thread_to_finish(id: str):
#         if threads[f"{id}"] is not None:
#             if threads[f"{id}"].is_alive():
#                 threads[f"{id}"].join()
#                 CLI.printline(Level.WARNING, f"(experiment mode)-waited {id}")

#     def get_ai_result(image, pnp_confidence):
#         global ai_result
#         ai_result = vision.PNP.is_egg_detected(image, pnp_confidence)
#         CLI.printline(Level.INFO, f"(Experiment)-ai done")

#     def comm_thread(BOARD: BScbAPI, image, tmp_egg_pot_counter, timestamp_of_image):
#         global ai_result
#         camera.CAMERA.save_raw_frame(image, 1, ai_result, timestamp_of_image)
#         with data.lock:
#             data.pot_processed += 1
#             data.pot_unloaded += tmp_egg_pot_counter

#     def _move_sw(BOARD: BScbAPI, lock: threading.Lock, star_wheel_move_time):
#         with lock:
#             BOARD.star_wheel_move_ms(star_wheel_move_time)

#     def _unload(BOARD: BScbAPI, lock: threading.Lock):
#         with lock:
#             BOARD.unload()

#     try:
#         # ====================================== Sense Check ===================================== #
#         if BOARD is None:
#             return
#         if not is_safe_to_move:
#             return

#         with data.lock:
#             _purge_counter = data.purge_counter

#         if _purge_counter >= 80:
#             # ============================ Read experiment pause state =========================== #
#             with data.lock:
#                 _experiment_pause_interval = data.experiment_pause_interval
#                 experiment_pause_state = data.experiment_pause_state

#             CLI.printline(Level.INFO, f"(experiment) Operation is in pause state: {experiment_pause_state}")

#             # ============================ Initialize new pause state ============================ #
#             if not experiment_pause_state:
#                 with data.lock:
#                     _new_experiment_pause_start_time = time.time()
#                     data.experiment_pause_start_time = _new_experiment_pause_start_time

#                 CLI.printline(
#                     Level.INFO, f"(experiment) New pause started at: {round(_new_experiment_pause_start_time, 2)}"
#                 )

#                 with data.lock:
#                     data.experiment_pause_state = True

#                 logging.info(
#                     f"Experiment mode in Pause State for {_experiment_pause_interval} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#                 )

#             # ============================== Calculate elapsed time ============================== #
#             with data.lock:
#                 _experiment_pause_start_time = data.experiment_pause_start_time

#             elapsed_time = time.time() - _experiment_pause_start_time

#             CLI.printline(
#                 Level.INFO,
#                 f"(experiment mode)- pause state - remaining time : {_experiment_pause_interval - elapsed_time} ",
#             )

#             with data.lock:
#                 data.experiment_status = f"pause state for {_experiment_pause_interval}s - remaining time : {_experiment_pause_interval - elapsed_time}s"

#             # ================================ Reset purge counter =============================== #
#             if elapsed_time > _experiment_pause_interval:
#                 with data.lock:
#                     data.purge_counter = 0
#                     data.experiment_pause_state = False

#         else:
#             wait_thread_to_finish("sw")
#             image = camera.CAMERA.get_frame()
#             timestamp_of_image = datetime.now()
#             CLI.printline(Level.INFO, f"(Experiment)-image captured")
#             wait_thread_to_finish("ul")
#             threads["sw"] = threading.Thread(
#                 target=_move_sw,
#                 args=(
#                     BOARD,
#                     lock,
#                     star_wheel_move_time,
#                 ),
#             )
#             threads["sw"].start()
#             CLI.printline(Level.INFO, f"(experiment mode)-sw moving")

#             # ======================================= AI thread ====================================== #
#             wait_thread_to_finish("ai")
#             threads["ai"] = threading.Thread(
#                 target=get_ai_result,
#                 args=(
#                     image,
#                     pnp_confidence,
#                 ),
#             )
#             threads["ai"].start()
#             CLI.printline(Level.INFO, f"(PnP)-ai started")

#             # ======================================= ul thread ====================================== #
#             wait_thread_to_finish("sw")
#             wait_thread_to_finish("ai")

#             # =================================== What is this =================================== #
#             # FIXME
#             # !data.purge_all_timer is initialized as None. This makes it that every first loop is an exception
#             with data.lock:
#                 _purge_all_timer = data.purge_all_timer
#                 _purge_counter = data.purge_counter

#             if _purge_all_timer is None:
#                 _purge_all_timer = time.time()

#             tmp_egg_pot_counter = 1 if (ai_result > 0 or (time.time() - _purge_all_timer) > 3600) else 0
#             if (time.time() - _purge_all_timer) > 3600 and _purge_counter == 80:
#                 with data.lock:
#                     data.purge_all_timer = time.time()

#             cloud.DataBase.data_update("egg" if ai_result > 0 else "noegg")
#             cloud.DataBase.data_upload()
#             if tmp_egg_pot_counter > 0:
#                 threads["ul"] = threading.Thread(
#                     target=_unload,
#                     args=(
#                         BOARD,
#                         lock,
#                     ),
#                 )
#                 threads["ul"].start()

#             # ====================================== comm thread ===================================== #
#             threads["comm"] = threading.Thread(
#                 target=comm_thread,
#                 args=(
#                     BOARD,
#                     image,
#                     # pnp_confidence,
#                     tmp_egg_pot_counter,
#                     timestamp_of_image,
#                 ),
#             )
#             threads["comm"].start()

#             # ============================== Increase purge counter ============================== #
#             with data.lock:
#                 _purge_counter = data.purge_counter + 1
#                 data.purge_counter = _purge_counter

#             CLI.printline(Level.INFO, f"(experiment mode)- purging state - pots unloaded : {_purge_counter} ")
#             data.experiment_status = f"purging state - pots unloaded : {_purge_counter}"
#             logging.info(
#                 f"Experiment mode in Purging State, pot unloaded :{_purge_counter} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#             )
#     except Exception as e:
#         CLI.printline(Level.ERROR, f"(experiment mode)-{e}")


def experiment(
    BOARD: BScbAPI, lock: threading.Lock, is_safe_to_move: bool, star_wheel_move_time: int, pnp_confidence: float
):
    global threads

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
        time_current = time.time()
        pot_is_overtime = BOARD.timer.is_it_overtime()  # is current pot overtime

        # ====================================== Sense Check ===================================== #
        if BOARD is None:
            return
        if not is_safe_to_move:
            return

        # =============================== Read experiment data =============================== #
        with data.lock:
            _experiment2_current_iteration = data.experiment2_current_iteration
            _experiment2_max_iteration = data.experiment2_max_iteration
            _experiment2_purge_iteration = data.experiment2_purge_iteration
            _experiment2_time_per_sequence = data.experiment2_time_per_sequence
            _experiment2_pot_counter = data.experiment2_pot_counter
            _experiment2_max_pot = data.experiment2_max_pot
            _experiment2_time_stamp = data.experiment2_time_stamp
            _experiment2_new_session = data.experiment2_new_session

        # ================================= Update time stamp ===================s============= #
        _dt = time_current - _experiment2_time_stamp

        # first init
        if _experiment2_new_session:
            if _dt > setup.EXPERIMENT_STAGGER_DELAY:
                with data.lock:
                    data.experiment2_time_stamp = time.time()
                    _experiment2_time_stamp = data.experiment2_time_stamp  # reassign time_stamp
                    data.experiment2_new_session = False
            else:
                with data.lock:
                    data.experiment_status = "[{:^10}-({})] - [{}/{}] slots - [{:^4}/{:^4}] mins".format(
                        "waiting",
                        _experiment2_current_iteration,
                        data.experiment2_pot_counter,
                        data.experiment2_max_pot,
                        round(_dt / 60, 2),
                        round(setup.EXPERIMENT_STAGGER_DELAY, 2),
                    )

        else:
            # reset pot counter and time slot on timeout
            if _dt > _experiment2_time_per_sequence:
                with data.lock:
                    data.experiment2_time_stamp = time.time()

                    # reset pot counter on new iteration
                    data.experiment2_pot_counter = 0
                    _experiment2_pot_counter = data.experiment2_pot_counter

                    # shift current iteration forward. Reset if = max (bounded from 0 - 4)
                    if data.experiment2_current_iteration >= _experiment2_max_iteration:
                        data.experiment2_current_iteration = 0
                    else:
                        data.experiment2_current_iteration += 1
                    _experiment2_current_iteration = data.experiment2_current_iteration  # reassign

            # ==================================================================================== #
            #                                         Move?                                        #
            # ==================================================================================== #
            # less than 80
            if _experiment2_pot_counter < _experiment2_max_pot:

                # ===================================== SW thread ==================================== #
                # Move starwheel
                wait_thread_to_finish("sw")
                image = camera.CAMERA.get_frame()
                timestamp_of_image = datetime.now()
                CLI.printline(Level.INFO, f"(experiment)-image captured")
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
                CLI.printline(Level.INFO, f"(experiment)-sw moving")

                # ======================================= AI thread ====================================== #
                # Run AI
                wait_thread_to_finish("ai")
                threads["ai"] = threading.Thread(
                    target=get_ai_result,
                    args=(
                        image,
                        pnp_confidence,
                    ),
                )
                threads["ai"].start()
                CLI.printline(Level.INFO, f"(experiment)-ai started")

                # ==================================== Upload data =================================== #
                cloud.DataBase.data_update("egg" if ai_result > 0 else "noegg")
                cloud.DataBase.data_upload()

                # ==================================== ul decision =================================== #
                # Unload if egg, overtime, or if is on purge iteration
                wait_thread_to_finish("sw")
                wait_thread_to_finish("ai")
                tmp_egg_pot_counter = 1 if (ai_result > 0 or pot_is_overtime) else 0

                if tmp_egg_pot_counter > 0 or (_experiment2_current_iteration == _experiment2_purge_iteration):
                    # Update egg timer on BOARD
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
                        # pnp_confidence,
                        tmp_egg_pot_counter,
                        timestamp_of_image,
                    ),
                )
                threads["comm"].start()

                # =============================== Increase slot counter ============================== #
                with data.lock:
                    # add 1
                    data.experiment2_pot_counter += 1
                    _experiment2_pot_counter = data.experiment2_pot_counter  # reassign

                    data.experiment_status = "[{:^10}-({})] - [{}/{}] slots - [{:^4}/{:^4}] mins".format(
                        "Purge" if _experiment2_current_iteration == _experiment2_purge_iteration else "AI",
                        _experiment2_current_iteration,
                        data.experiment2_pot_counter,
                        data.experiment2_max_pot,
                        round(_dt / 60, 2),
                        round(data.experiment2_time_per_sequence / 60, 2),
                    )

                # ===================================== Log state ==================================== #
                logging.info(
                    "Experiment mode in {}({}) State, pot unloaded :{} at {}".format(
                        "Purge" if _experiment2_current_iteration == _experiment2_purge_iteration else "AI",
                        _experiment2_current_iteration,
                        _experiment2_pot_counter,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                )

            else:
                # more than 80
                with data.lock:
                    data.experiment_status = "[{:^10}-({})] - [{}/{}] slots - [{:^4}/{:^4}] mins".format(
                        "Purge" if _experiment2_current_iteration == _experiment2_purge_iteration else "AI",
                        _experiment2_current_iteration,
                        data.experiment2_pot_counter,
                        data.experiment2_max_pot,
                        round(_dt / 60, 2),
                        round(data.experiment2_time_per_sequence / 60, 2),
                    )

    except Exception as e:
        CLI.printline(Level.ERROR, f"(experiment)-{e}")


timestamp: time.time = 0


def need_unload_in_interval(is_prev_unloaded: bool, interval_s: float = 5.0):
    global timestamp
    current = timestamp
    res = (time.time() - current) > interval_s
    if is_prev_unloaded or res:
        timestamp = time.time()
    return res
