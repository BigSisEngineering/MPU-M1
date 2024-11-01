import threading
import time
import json

# ------------------------------------------------------------------------------------ #
from src import components

# ------------------------------------------------------------------------------------ #
from src._shared_variables import Cages, SV

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "CAGE_SCORE"


MAX_SLOTS_ACROSS_CAGES: int = 14 * 80  # 14 Cages * 80 SW Slots


class CageScore:
    def __init__(self):
        self._cage_score_lock = threading.Lock()
        self._cage_score = {
            "completed_num": None,
            "completed_score": None,
            "min_num": None,
            "min_score": None,
            "max_num": None,
            "max_score": None,
        }

        # for storage
        self._storage_dict = {}

        # update thread
        self._thread = threading.Thread(target=self.__loop)

    def __create_new_key(self, sequence_number: int):
        self._storage_dict[sequence_number] = {cage: 0 for cage in Cages}

    def __update_data(self):
        # Get experiment dict
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
        _min_sequence_number = None
        _max_sequence_number = None
        _more_than_one_active: bool = False

        if len(_active_sequence_list) > 1:
            _more_than_one_active = True

        # Ongoing
        for index, value in enumerate(_active_sequence_list):
            _min_sequence_number = min(_min_sequence_number, value) if not _min_sequence_number is None else value
            _max_sequence_number = max(_max_sequence_number, value) if not _max_sequence_number is None else value

        # Completed
        _completed_sequence_number = _min_sequence_number - 1

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
        if _completed_sequence_number in self._storage_dict:
            _slots_by_sequence_number_dict = self._storage_dict[_completed_sequence_number]

            # Get total slots
            for cage in Cages:
                _total_slots_completed += _slots_by_sequence_number_dict[cage]

            # Compute score (rounded to 2dp)
            _this_score_completed = round(_total_slots_completed / MAX_SLOTS_ACROSS_CAGES * 100, 2)

        else:
            _completed_session_exist = False

        # ================== Compute score for ongoing sequence number (min) ================= #
        _slots_by_sequence_number_dict = self._storage_dict[_min_sequence_number]

        # Get total slots
        for cage in Cages:
            _total_slots_min += _slots_by_sequence_number_dict[cage]

        # Compute score (rounded to 2dp)
        _this_score_min = round(_total_slots_min / MAX_SLOTS_ACROSS_CAGES * 100, 2)

        # ================== Compute score for ongoing sequence number (max) ================= #
        # only compute if more than 1 active session
        if _more_than_one_active:
            _slots_by_sequence_number_dict = self._storage_dict[_max_sequence_number]

            # Get total slots
            for cage in Cages:
                _total_slots_max += _slots_by_sequence_number_dict[cage]

            # Compute score (rounded to 2dp)
            _this_score_max = round(_total_slots_max / MAX_SLOTS_ACROSS_CAGES * 100, 2)

        # ==================================================================================== #
        #                                   Assign to UI dict                                  #
        # ==================================================================================== #
        with self._cage_score_lock:
            self._cage_score = {
                "completed_num": _completed_sequence_number if _completed_session_exist else None,
                "completed_score": _this_score_completed if _completed_session_exist else None,
                "completed_slots": _total_slots_completed if _completed_session_exist else None,
                "min_num": _min_sequence_number,
                "min_score": _this_score_min,
                "min_slots": _total_slots_min,
                "max_num": _max_sequence_number if _more_than_one_active else None,
                "max_score": _this_score_max if _more_than_one_active else None,
                "max_slots": _total_slots_max if _more_than_one_active else None,
            }

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
                self.__update_data()
                time_stamp = time.time()
        CLI.printline(Level.INFO, "({:^10}) End".format(print_name))

    # ------------------------------------------------------------------------------------ #
    def start(self):
        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))
        self._thread.start()
