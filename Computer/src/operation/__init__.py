import random
import time
import threading
from typing import Dict
from datetime import datetime
import logging

# ------------------------------------------------------------------------------------------------ #
from src import data, cloud
from src.tasks import camera
from src.BscbAPI.BscbAPI import BScbAPI
from src import vision
from src import CLI
from src.CLI import Level


purge_state: int = 0
sw_thread: threading.Thread = None
unload_thread: threading.Thread = None
star_wheel_move_time: int = data.star_wheel_duration_ms
ai_result = 0
unloaded: bool = False
threads: Dict[str, threading.Thread] = {
    "sw": None,
    "ul": None,
    "ai": None,
    "comm": None,
}
counter = 0


def pnp(
    BOARD: BScbAPI,
    lock: threading.Lock,
    is_safe_to_move: bool,
    star_wheel_move_time: int,
    pnp_confidence: float,
):
    global threads, unloaded

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
        if ai_result <= 0 and pot_is_overtime:
            camera.CAMERA.save_raw_frame(image, 0, 0, timestamp_of_image)
        else:
            camera.CAMERA.save_raw_frame(image, pnp_confidence, ai_result, timestamp_of_image)
        with data.lock:
            data.pot_processed += 1

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

        # ============================ Set new timer for fresh pot =========================== #
        if unloaded:
            # Assume pot loaded because 'is_safe_to_move'
            BOARD.timer.update_slot()

        wait_thread_to_finish("sw")
        pot_is_overtime = BOARD.timer.is_it_overtime()

        # ======================================== Camera ======================================== #
        image = camera.CAMERA.get_frame()
        timestamp_of_image = datetime.now()
        CLI.printline(Level.INFO, f"(PnP)-image captured")

        # ======================================= sw thread ====================================== #
        wait_thread_to_finish("ul")

        # move starwheel
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

        tmp_egg_pot_counter = 1 if (ai_result > 0 or pot_is_overtime) else 0
        if tmp_egg_pot_counter > 0:

            # Use timer if not model v10 with crack detection
            # if data.model != "v10":
            #     BOARD.timer.update_slot()

            unloaded = True

            with data.lock:
                data.pot_unloaded += 1  # request pot

            threads["ul"] = threading.Thread(
                target=_unload,
                args=(
                    BOARD,
                    lock,
                ),
            )
            threads["ul"].start()
        else:
            unloaded = False

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

        # ==================================== data upload =================================== #
        _data = "other" if pot_is_overtime else ("egg" if ai_result > 0 else "noegg")
        cloud.DataBase.data_update(_data)
        cloud.DataBase.data_upload()

        # Use timer if not model v10 with crack detection
        # if data.model != "v10":
        #     BOARD.timer.move_index()

    except Exception as e:
        CLI.printline(Level.ERROR, f"(PnP)-{e}")


def dummy(
    BOARD: BScbAPI,
    lock: threading.Lock,
    is_safe_to_move: bool,
    star_wheel_move_time: int,
    unload_probability: float,
):
    global threads, counter, unloaded

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

        # ============================ Set new timer for fresh pot =========================== #
        if unloaded:
            # Assume pot loaded because 'is_safe_to_move'
            BOARD.timer.update_slot()

        # ==================================== Do nothing ==================================== #
        wait_thread_to_finish("sw")

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
        if tmp_egg_pot_counter > 0:
            unloaded = True

            with data.lock:
                data.pot_unloaded += 1  # request pot

            threads["ul"] = threading.Thread(
                target=_unload,
                args=(
                    BOARD,
                    lock,
                ),
            )
            threads["ul"].start()
        else:
            unloaded = False

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
#

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

#             # ============================== Calculate sequence_elapsed time ============================== #
#             with data.lock:
#                 _experiment_pause_start_time = data.experiment_pause_start_time

#             sequence_elapsed_time = time.time() - _experiment_pause_start_time

#             CLI.printline(
#                 Level.INFO,
#                 f"(experiment mode)- pause state - remaining time : {_experiment_pause_interval - sequence_elapsed_time} ",
#             )

#             with data.lock:
#                 data.experiment_status = f"pause state for {_experiment_pause_interval}s - remaining time : {_experiment_pause_interval - sequence_elapsed_time}s"

#             # ================================ Reset purge counter =============================== #
#             if sequence_elapsed_time > _experiment_pause_interval:
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
    BOARD: BScbAPI,
    lock: threading.Lock,
    is_safe_to_move: bool,
    star_wheel_move_time: int,
    pnp_confidence: float,
):
    global threads, unloaded

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

    def _move_sw(BOARD: BScbAPI, lock: threading.Lock, star_wheel_move_time):
        with lock:
            BOARD.star_wheel_move_ms(star_wheel_move_time)

    def _unload(BOARD: BScbAPI, lock: threading.Lock):
        with lock:
            BOARD.unload()

    try:
        # ================================= Get current time ================================= #
        _time_now = datetime.now()
        total_seconds = (_time_now.hour * 3600) + (_time_now.minute * 60) + _time_now.second

        # ================================== Read user input ================================= #
        with data.lock:
            _sequence_duration = data.sequence_duration
            _interval = data.interval
            _purge_frequency = data.purge_frequency
            _experiment2_pot_counter = data.experiment2_pot_counter
            _experiment2_previous_sequence_number = data.experiment2_previous_sequence_number

        # ========================== Compute Current Sequence Number ========================= #
        # Current sequence number. This number will continue to increase until it resets at midnight.
        _current_sequence_number = total_seconds // _sequence_duration

        # =================================== Time elapsed =================================== #
        # Time elapsed from current sequence (no offset).
        _sequence_elapsed = total_seconds % _sequence_duration

        # Time elapsed from current sequence (offset to cage)
        dt = (_sequence_elapsed - (data.cage_number - 1) * _interval) % _sequence_duration

        with data.lock:
            data.time_elapsed = dt  # for UI

        # ==================================== Toggle now? =================================== #
        # The cage number that should toggle now. Value is from 0-13
        _cage_starting = _sequence_elapsed // _interval

        # Create new session now if this is the current cage
        _create_new_session_now: bool = _cage_starting >= (data.cage_number - 1)

        # =================================== New Session? =================================== #
        _sequence_number_changed: bool = _experiment2_previous_sequence_number != _current_sequence_number

        if _sequence_number_changed and _create_new_session_now:
            with data.lock:
                # reset pot counter on new iteration
                data.experiment2_pot_counter = 0
                _experiment2_pot_counter = data.experiment2_pot_counter

                # update previous sequence number
                data.experiment2_previous_sequence_number = _current_sequence_number

        # ==================================== Ai / Purge? =================================== #
        # Time shift
        _total_seconds_shifted = total_seconds - (data.cage_number - 1) * _interval

        # Cage sequence index (mapped down to 0-4)
        _cage_sequence_index = (_total_seconds_shifted // _sequence_duration) % _purge_frequency

        # Is cage on its purge sequence index?
        _cage_purge_sequence_index = (data.cage_number - 1) % _purge_frequency

        # Purge now
        _purge_now: bool = _cage_sequence_index == _cage_purge_sequence_index

        # ======================== Compute index for master UI display ======================= #
        # Map index to 0-4
        # 0-ai
        # 1-ai
        # 2-ai
        # 3-ai
        # 4-purge
        _index_shift = (_purge_frequency - 1) - _cage_purge_sequence_index
        with data.lock:
            data.index_ui = (_cage_sequence_index + _index_shift) % _purge_frequency

        # ==================================== Sense check =================================== #
        if not is_safe_to_move or BOARD is None:
            # Keep updating the report
            # more than 80
            with data.lock:  # for cage UI
                data.experiment_status = "[{:^10}-({})] - [{}/{}] slots - [{:^4}/{:^4}] mins".format(
                    ("Purge" if _purge_now else f"AI") + f"({_cage_sequence_index})",
                    _current_sequence_number,
                    data.experiment2_pot_counter,
                    data.STARWHEEL_SLOTS,
                    round(dt / 60, 2),
                    round(_sequence_duration / 60, 2),
                )
            return

        # ============================ Set new timer for fresh pot =========================== #
        if unloaded:
            # Assume pot loaded because 'is_safe_to_move'
            BOARD.timer.update_slot()

        # ==================================================================================== #
        #                                         Move?                                        #
        # ==================================================================================== #
        # less than 80
        if _experiment2_pot_counter < data.STARWHEEL_SLOTS:

            wait_thread_to_finish("sw")
            pot_is_overtime = BOARD.timer.is_it_overtime()  # is current pot overtime

            # ================================ Start blasting air ================================ #
            CLI.printline(Level.ERROR, f"(experiment)-VALVE ON")
            BOARD.valve_turn_on()

            # ==================================== Take image ==================================== #
            image = camera.CAMERA.get_frame()
            timestamp_of_image = datetime.now()
            CLI.printline(Level.INFO, f"(experiment)-image captured")
            wait_thread_to_finish("ul")

            # ===================================== SW thread ==================================== #
            # Get details for pot at unload position

            # Move starwheel
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
            wait_thread_to_finish("sw")
            wait_thread_to_finish("ai")

            # upload new AI result
            cloud.DataBase.data_update("egg" if ai_result > 0 else "noegg")
            cloud.DataBase.data_upload()

            # ==================================== ul decision =================================== #
            # Unload if previous result is egg, overtime, or if is on purge iteration
            tmp_egg_pot_counter = 1 if (ai_result > 0 or pot_is_overtime or _purge_now) else 0

            if tmp_egg_pot_counter > 0:
                unloaded = True

                with data.lock:
                    data.pot_unloaded += 1  # request pot

                threads["ul"] = threading.Thread(
                    target=_unload,
                    args=(
                        BOARD,
                        lock,
                    ),
                )
                threads["ul"].start()
            else:
                unloaded = False

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

                # for cage UI
                data.experiment_status = "[{:^10}-({})] - [{}/{}] slots - [{:^4}/{:^4}] mins".format(
                    ("Purge" if _purge_now else f"AI") + f"({_cage_sequence_index})",
                    _current_sequence_number,
                    data.experiment2_pot_counter,
                    data.STARWHEEL_SLOTS,
                    round(dt / 60, 2),
                    round(_sequence_duration / 60, 2),
                )

            # ===================================== Log state ==================================== #
            logging.info(
                "Experiment mode in {}({})-{}[{}] State, pot unloaded :{} at {}".format(
                    ("Purge" if _purge_now else f"AI") + f"({_current_sequence_number})",
                    _cage_sequence_index,
                    _cage_purge_sequence_index,
                    data.experiment2_pot_counter,
                    _experiment2_pot_counter,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
            )

        else:
            # ================================= Stop blasting air ================================ #
            BOARD.valve_turn_off()

            # more than 80
            with data.lock:
                data.experiment_status = "[{:^10}-({})] - [{}/{}] slots - [{:^4}/{:^4}] mins".format(
                    ("Purge" if _purge_now else f"AI") + f"({_cage_sequence_index})",
                    _current_sequence_number,
                    data.experiment2_pot_counter,
                    data.STARWHEEL_SLOTS,
                    round(dt / 60, 2),
                    round(_sequence_duration / 60, 2),
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
