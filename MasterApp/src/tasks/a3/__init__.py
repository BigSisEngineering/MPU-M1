import threading
import time
from typing import Optional, Dict

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
        self.__lock_status = threading.Lock()
        self.__status: Status = Status()

        #
        self.__lock_accumulated_pots = threading.Lock()
        self.__accumulated_pots: int = 0
        self.__set_zero_flag: bool = False

        #
        self.lock_num_pots = threading.Lock()
        self.num_pots: int = 0

        self.loop_thread = threading.Thread(target=self.__loop, daemon=True)
        self.worker_thread = threading.Thread(target=self.__fetch_num_pots, daemon=True)

    @property
    def status(self):
        with self.__lock_status:
            r = self.__status
        return r.dict()

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
                global_variables = components.A3.fetch_global_variables()

                is_sw_homed = global_variables[GlobalVars.SW_HOMED] == 1
                is_running = global_variables[GlobalVars.RUN] == 1
                is_sending_pots = global_variables[GlobalVars.IS_RUNNING] == 1
                remaining = global_variables[GlobalVars.REMAINING]

                # =================================== Fetch sensors ================================== #
                sensor_readings = components.A3.read_object("sensors.gpIn")

                is_sw_error = sensor_readings[Sensors.SW_ERROR]["value"] == 1
                is_buff_in_full = sensor_readings[Sensors.BUFF_IN]["value"] == 1
                has_pot = sensor_readings[Sensors.POT_PRESENCE]["value"] == 1

                # =================================== Update Status ================================== #

                with self.__lock_status:
                    self.__status.connected = True
                    self.__status.sw_error = is_sw_error
                    self.__status.sw_homed = is_sw_homed
                    self.__status.buff_in = is_buff_in_full
                    self.__status.pot_sensor = has_pot

                # ======================================= Run? ======================================= #
                if SV.run_1a:
                    # Update Status
                    with self.__lock_status:
                        self.__status.running = True

                    # Start belts
                    if not is_running:
                        components.A3.start()
                    else:
                        # System ready?
                        if not is_sending_pots and is_buff_in_full and not is_sw_error and is_sw_homed:
                            # > Pulse Time?
                            if pulse_timer.send_now:
                                # Reset 'remaing' on duet
                                components.A3.reset_remaining()

                                # Pass previously read 'remaining'
                                self.__send_pulse(remaining)

                else:
                    # Update Status
                    with self.__lock_status:
                        self.__status.running = False

                    # Stop belts
                    if is_running:
                        components.A3.reset_remaining()
                        components.A3.stop()

            except Exception as e:
                # default value
                with self.__lock_status:
                    self.__status = Status()

                CLI.printline(Level.ERROR, "({:^10}) {}".format(print_name, e))

    # ==================================================================================== #
    #                                         Pulse                                        #
    # ==================================================================================== #
    def __get_pot_worker(self, cage) -> None:
        result = components.cage_dict[cage].fetch_pot_data()
        with self.lock_num_pots:
            self.num_pots += result

        # prevent flush
        time.sleep(SV.PULSE_INTERVAL)

    def __fetch_num_pots(self) -> int:
        # initialize
        threads: Dict[Cages, threading.Thread] = {
            cage: threading.Thread(target=self.__get_pot_worker, args=(cage,), daemon=True) for cage in Cages
        }
        while True:
            for cage in Cages:
                if not threads[cage].is_alive():
                    threads[cage] = threading.Thread(target=self.__get_pot_worker, args=(cage,), daemon=True)
                    threads[cage].start()

    def __send_pulse(self, remaining: int) -> bool:
        try:
            # =================================== Get num pots =================================== #
            with self.lock_num_pots:
                num_pots = self.num_pots
                self.num_pots = 0

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
        self.worker_thread.start()
