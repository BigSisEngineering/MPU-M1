import threading

from src import components
from src.components.a1_pot_sorter import Status, Sensors
from src._shared_variables import SV
from src.utils import WarningTimer

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "POT_SORTER"


class StatusCode:
    IDLE = 0
    OFFLINE = 1
    FILLING = 2
    FILLING_TIMEOUT = 3  # empty for too long
    FULL = 4
    FULL_TIMEOUT = 5  # full for too long
    STOPPING = 6
    STARTING = 7


class Task:
    def __init__(self):
        self.__lock_status = threading.Lock()
        self.__status: Status = Status()

        self.__lock_status_code = threading.Lock()
        self.__status_code: StatusCode = StatusCode.OFFLINE

        self.loop_thread = threading.Thread(target=self.__loop, daemon=True)

    @property
    def status(self):
        dict = {}
        with self.__lock_status:
            r = self.__status

        dict = r.dict()
        dict["status_code"] = self.status_code
        return dict

    @property
    def status_code(self):
        with self.__lock_status_code:
            r = self.__status_code
        return r

    def __update_status_code(self, code: StatusCode):
        with self.__lock_status_code:
            self.__status_code = code

    def __loop(self):
        buff_out_empty_timer: WarningTimer = WarningTimer(30)
        buff_out_full_timer: WarningTimer = WarningTimer(30)

        while True:
            try:
                # =================================== Fetch Sensors ================================== #
                sensor_readings = components.A1.read_object("sensors.gpIn")
                is_buff_out_triggered = sensor_readings[Sensors.BUFF_OUT]["value"] == 1

                # =================================== Fetch Status =================================== #
                is_running = not components.A1.is_idle

                # =================================== Update Status ================================== #
                with self.__lock_status:
                    self.__status.connected = True
                    self.__status.running = is_running
                    self.__status.buff_out = is_buff_out_triggered

                # =================================== Reset Timers? ================================== #
                # is buff out triggered? (the hope is that it can detect pots passing through)
                if is_buff_out_triggered:
                    # reset empty timer if full
                    buff_out_empty_timer.reset_timer()
                else:
                    # reset full timer if empty
                    buff_out_full_timer.reset_timer()

                # ======================================= Run? ======================================= #
                if SV.run_1a:
                    if not is_running:
                        # update status code
                        self.__update_status_code(StatusCode.STARTING)

                        # reset timer
                        buff_out_empty_timer.reset_timer()
                        buff_out_full_timer.reset_timer()

                        # start a1
                        components.A1.start()
                    else:
                        if is_buff_out_triggered:
                            # is full for too long?
                            if buff_out_full_timer.is_overtime:
                                self.__update_status_code(StatusCode.FULL_TIMEOUT)
                            else:
                                self.__update_status_code(StatusCode.FULL)
                        else:
                            # is empty for too long?
                            if buff_out_empty_timer.is_overtime:
                                self.__update_status_code(StatusCode.FILLING_TIMEOUT)
                            else:
                                self.__update_status_code(StatusCode.FILLING)

                else:
                    if is_running:
                        self.__update_status_code(StatusCode.STOPPING)
                        components.A1.stop()
                    else:
                        self.__update_status_code(StatusCode.IDLE)

            except Exception as e:
                # default value
                with self.__lock_status:
                    self.__status = Status()

                self.__update_status_code(StatusCode.OFFLINE)

                CLI.printline(Level.ERROR, "({:^10}) {}".format(print_name, e))

    def start(self):
        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))
        self.loop_thread.start()
