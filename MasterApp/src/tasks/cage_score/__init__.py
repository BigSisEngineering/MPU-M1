import threading
import time
import json
from datetime import datetime

# ------------------------------------------------------------------------------------ #
from src import components

# ------------------------------------------------------------------------------------ #
from src._shared_variables import Cages, SV

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "CAGE_SCORE"


MAX_SLOTS_ACROSS_CAGES: int = 14 * 80  # 14 Cages * 80 SW Slots


class Task:
    def __init__(self):
        self._cage_score_lock = threading.Lock()
        self._cage_score = {
            "completed_num": None,
            "completed_score": None,
            "completed_slots": None,
            "min_num": None,
            "min_score": None,
            "min_slots": None,
            "max_num": None,
            "max_score": None,
            "max_slots": None,
            "best_num": None,
            "best_score": None,
            "best_slots": None,
        }
        # for daily reset
        self._previous_total_seconds = 0

        # for storage
        self._storage_dict = {}

        # update thread
        self._thread = threading.Thread(target=self.__loop)

    def __create_new_key(self, sequence_number: int):
        self._storage_dict[sequence_number] = {cage: 0 for cage in Cages}

    def __update_best_session(self, num, score, slots):
        with self._cage_score_lock:
            _best_score = self._cage_score["best_score"]

        # handle initialization
        if _best_score is None:
            with self._cage_score_lock:
                self._cage_score["best_num"] = num
                self._cage_score["best_score"] = score
                self._cage_score["best_slots"] = slots
            return

        if score > _best_score:
            with self._cage_score_lock:
                self._cage_score["best_num"] = num
                self._cage_score["best_score"] = score
                self._cage_score["best_slots"] = slots

    def __update_data(self):
        # ==================================== Daily Reset =================================== #
        _time_now = datetime.now()
        total_seconds = (_time_now.hour * 3600) + (_time_now.minute * 60) + _time_now.second

        if total_seconds < self._previous_total_seconds:
            # clear storage dict
            self._storage_dict.clear()

            with self._cage_score_lock:
                self._cage_score.clear()
                self._cage_score = {
                    "completed_num": None,
                    "completed_score": None,
                    "completed_slots": None,
                    "min_num": None,
                    "min_score": None,
                    "min_slots": None,
                    "max_num": None,
                    "max_score": None,
                    "max_slots": None,
                    "best_num": None,
                    "best_score": None,
                    "best_slots": None,
                }

        # update time stamp
        self._previous_total_seconds = total_seconds

        # ================================== Get dictionary ================================== #
        """
        "max_slots": 80,
        "operation_index": 0,
        "sequence_duration": 840,
        "sequence_number": -1,
        "slots": 0,
        "time_elapsed": 0
        """

        # Read data
        _experiment_dict = components.generate_cage_experiment_dict(raw_dict=True)

        # Init
        _active_sequence_list = []

        # ============================= Read latest slots by cage ============================ #
        for cage in Cages:
            _hostname = cage.value
            _cage_sequence_number = _experiment_dict[_hostname]["sequence_number"]

            # If is equal to the latest slot
            if isinstance(_cage_sequence_number, int):
                # append to active sequence
                if not _cage_sequence_number in _active_sequence_list:
                    _active_sequence_list.append(_cage_sequence_number)

                # Create new key
                if not _cage_sequence_number in self._storage_dict:
                    self.__create_new_key(_cage_sequence_number)

                # Assign value
                _slots_processed = _experiment_dict[_hostname]["slots"]
                if isinstance(_slots_processed, int):
                    self._storage_dict[_cage_sequence_number][cage] = _slots_processed

        # ========================== Find completed sequence number ========================== #
        _sequence_number_min = None
        _sequence_number_max = None
        _more_than_one_active: bool = False

        if len(_active_sequence_list) > 1:
            _more_than_one_active = True

        # filter unwanted sessions due to cage pause
        while len(_active_sequence_list) > (14 // 5):
            _min_value = None

            for index, value in enumerate(_active_sequence_list):
                _min_value = min(_sequence_number_min, value) if not _min_value is None else value

            _active_sequence_list.remove(_min_value)

        # Ongoing
        for index, value in enumerate(_active_sequence_list):
            if value < 0:
                # Filter -1 (init int assignment)
                break

            _sequence_number_min = min(_sequence_number_min, value) if not _sequence_number_min is None else value
            _sequence_number_max = max(_sequence_number_max, value) if not _sequence_number_max is None else value

        # Completed
        _sequence_number_completed = _sequence_number_min - 1

        # ==================================================================================== #
        #                                     Compute Score                                    #
        # ==================================================================================== #
        _total_slots_completed = 0
        _this_score_completed = 0
        _total_slots_min = 0
        _this_score_min = 0
        _total_slots_max = 0
        _this_score_max = 0

        _completed_session_exist: bool = True

        # ================= Compute score for last completed sequence number ================= #
        if _sequence_number_completed in self._storage_dict:
            _slots_by_sequence_number_dict = self._storage_dict[_sequence_number_completed]

            # Get total slots
            for cage in Cages:
                _total_slots_completed += _slots_by_sequence_number_dict[cage]

            # Compute score (rounded to 2dp)
            _this_score_completed = round(_total_slots_completed / MAX_SLOTS_ACROSS_CAGES * 100, 2)

            # Update best session
            self.__update_best_session(_sequence_number_completed, _this_score_completed, _total_slots_completed)

        else:
            _completed_session_exist = False

        # ================== Compute score for ongoing sequence number (min) ================= #
        _slots_by_sequence_number_dict = self._storage_dict[_sequence_number_min]

        # Get total slots
        for cage in Cages:
            _total_slots_min += _slots_by_sequence_number_dict[cage]

        # Compute score (rounded to 2dp)
        _this_score_min = round(_total_slots_min / MAX_SLOTS_ACROSS_CAGES * 100, 2)

        # Update best session
        self.__update_best_session(_sequence_number_min, _this_score_min, _total_slots_min)

        # ================== Compute score for ongoing sequence number (max) ================= #
        # only compute if more than 1 active session
        if _more_than_one_active:
            _slots_by_sequence_number_dict = self._storage_dict[_sequence_number_max]

            # Get total slots
            for cage in Cages:
                _total_slots_max += _slots_by_sequence_number_dict[cage]

            # Compute score (rounded to 2dp)
            _this_score_max = round(_total_slots_max / MAX_SLOTS_ACROSS_CAGES * 100, 2)

            # Update best session
            self.__update_best_session(_sequence_number_max, _this_score_max, _total_slots_max)

        # ==================================================================================== #
        #                                   Assign to UI dict                                  #
        # ==================================================================================== #
        with self._cage_score_lock:
            self._cage_score["completed_num"] = _sequence_number_completed if _completed_session_exist else None
            self._cage_score["completed_score"] = (_this_score_completed if _completed_session_exist else None,)
            self._cage_score["completed_slots"] = (_total_slots_completed if _completed_session_exist else None,)
            self._cage_score["min_num"] = _sequence_number_min
            self._cage_score["min_score"] = _this_score_min
            self._cage_score["min_slots"] = _total_slots_min
            self._cage_score["max_num"] = (_sequence_number_max if _more_than_one_active else None,)
            self._cage_score["max_score"] = (_this_score_max if _more_than_one_active else None,)
            self._cage_score["max_slots"] = (_total_slots_max if _more_than_one_active else None,)

    # Get Status
    def get_cage_score(self, raw_dict=False):
        with self._cage_score_lock:
            r = self._cage_score

        if raw_dict:
            return r
        return json.dumps(r).encode()

    def __loop(self):
        time_stamp = time.time() - 300
        while not SV.KILLER_EVENT.is_set():
            if time.time() - time_stamp > SV.WATCHDOG:
                try:
                    self.__update_data()

                except Exception as e:
                    CLI.printline(Level.ERROR, "({:^10}) Error -> {}".format(print_name, e))

                time_stamp = time.time()
        CLI.printline(Level.INFO, "({:^10}) End".format(print_name))

    # ------------------------------------------------------------------------------------ #
    def start(self):
        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))
        self._thread.start()
