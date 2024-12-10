import threading
import time
from typing import List

from src import components
from src.components.a3_pot_dispenser import Status, Sensors, GlobalVars
from src._shared_variables import SV, Cages

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "POT DISP"


class PulseTimer:
    def __init__(self, interval: float):
        self.time_stamp = time.time()
        self.interval = interval

    @property
    def send_now(self):
        if time.time() - self.time_stamp > self.interval:
            # update timestamp
            self.time_stamp = time.time()
            return True
        return False


class Task:
    def __init__(self):
        self.lock_status = threading.Lock()
        self.status: Status = Status()

        #
        self.__lock_accumulated_pots = threading.Lock()
        self.__accumulated_pots: int = 0
        self.__set_zero_flag: bool = False

        #
        self.lock_num_pots = threading.Lock()
        self.num_pots: int = 0

        # -------------------------------------------------------- #
        self.loop_thread = threading.Thread(target=self.__loop, daemon=True)

    @property
    def status(self):
        with self.lock_status:
            status = self.status
        return status.dict()

    # ------------------------------------------------------------------------------------ #
    @property
    def accumulated_pots(self) -> int:
        with self.__lock_accumulated_pots:
            __accumulated_pots = self.__accumulated_pots
        return __accumulated_pots

    def add_pots(self, w: int) -> str:
        with self.__lock_accumulated_pots:
            self.__accumulated_pots = self.__accumulated_pots + w
        return "Added {:^3} pots".format(w)

    def set_zero(self) -> str:
        with self.__lock_accumulated_pots:
            self.__accumulated_pots = 0

        self.__set_zero_flag = True
        return f"Accumulated pots -> 0."

    # ------------------------------------------------------------------------------------ #
    def __loop(self) -> None:
        pulse_interval = SV.PULSE_INTERVAL
        pulse_timer: PulseTimer = PulseTimer(pulse_interval)

        while True:
            try:
                # =================================== Fetch global =================================== #
                global_variables = components.A2.fetch_global_variables()

                is_sw_homed = global_variables[GlobalVars.SW_HOMED]
                is_running = global_variables[GlobalVars.RUN]
                is_sending_pots = global_variables[GlobalVars.IS_RUNNING]
                remaining = global_variables[GlobalVars.REMAINING]

                # =================================== Fetch sensors ================================== #
                sensor_readings = components.A2.read_object("sensors.gpIn")

                is_sw_error = sensor_readings[Sensors.SW_ERROR]["value"] == 1
                is_buff_in_full = sensor_readings[Sensors.BUFF_IN]["value"] == 1
                has_pot = sensor_readings[Sensors.POT_PRESENCE]["value"] == 1

                # =================================== Update Status ================================== #

                with self.lock_status:
                    self.status.connected = True
                    self.status.sw_error = is_sw_error
                    self.status.sw_homed = is_sw_homed
                    self.status.buff_in = is_buff_in_full
                    self.status.pot_sensor = has_pot

                # ======================================= Run? ======================================= #
                if SV.run_1a:
                    # Update Status
                    with self.lock_status:
                        self.status.running = True

                    # Start belts
                    if not is_running:
                        components.A3.start()
                    else:
                        # System ready?
                        if not is_sending_pots and is_buff_in_full:
                            # > Pulse Time?
                            if pulse_timer.send_now:
                                # Reset 'remaing' on duet
                                components.A3.reset_remaining()

                                # Pass previously read 'remaining'
                                self.__send_pulse(remaining)

                else:
                    # Update Status
                    with self.lock_status:
                        self.status.running = False

                    # Stop belts
                    if is_running:
                        components.A3.reset_remaining()
                        components.A3.stop()

            except Exception as e:
                # default value
                with self.lock_status:
                    self.status = Status()

                CLI.printline(Level.ERROR, "({:^10}) {}".format(print_name, e))

    # ==================================================================================== #
    #                                         Pulse                                        #
    # ==================================================================================== #
    def __get_pot_worker(self, cage) -> None:
        result = components.cage_dict[cage].fetch_pot_data()
        with self.lock_num_pots:
            self.num_pots += result

    def __get_num_pots(self) -> int:
        threads: List[threading.Thread] = []

        # ================================== Fetch pot data ================================== #
        for cage in Cages:
            threads.append(threading.Thread(target=self.__get_pot_worker, args=(cage,), daemon=True))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # ===================================== Get total ==================================== #
        with self.lock_num_pots:
            num_pots = self.num_pots
            self.num_pots = 0

        return num_pots

    def __send_pulse(self, remaining: int) -> bool:
        try:
            # ================================ Fetch Pot Requests ================================ #
            num_pots = self.__get_num_pots()

            # ================================ Set Zero Requested? =============================== #
            if self.__set_zero_flag:  # reset
                remaining = 0
                self.__set_zero_flag = False

            # ====================================== Compute ===================================== #
            # add [ current + accumulated + previously_not_sent ]
            __total_capsules = num_pots + self.accumulated_pots + remaining

            # ======================================= Send ======================================= #
            if components.A3.send_capsules(__total_capsules):
                # Reset
                with self.__lock_accumulated_pots:
                    self.__accumulated_pots = 0
            else:
                # Add pots if not executed (Shouldn't come to this)
                with self.__lock_accumulated_pots:
                    self.__accumulated_pots = num_pots

        except Exception as e:
            CLI.printline(Level.ERROR, "{:^10}-{:^15} Exception -> {}".format(print_name, "SEND PULSE", e))

    def start(self) -> None:
        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))
        self.loop_thread.start()
