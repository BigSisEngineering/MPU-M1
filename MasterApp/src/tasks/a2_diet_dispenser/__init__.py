import threading

from src import components
from src.components.a2_diet_dispenser import Status, Sensors, GlobalVars
from src import data
from src._shared_variables import SV
from src.utils import WarningTimer

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "DIET_DSP"


class StatusCode:
    IDLE = 0
    OFFLINE = 1
    DISPENSING = 2
    WAITING_BUF_IN = 3
    WAITING_BUF_IN_TIMEOUT = 4  # wait buff in for too long
    WAITING_BUF_OUT = 5
    STOPPING = 6
    STARTING = 7
    SW_ERROR = 8
    SW_NOT_HOMED = 9
    DISPENSER_NOT_HOMED = 10
    SW_HOMING = 11


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
        buff_in_empty_timer = WarningTimer(30)

        while True:
            try:
                # =================================== Fetch global =================================== #
                global_variables = components.A2.fetch_global_variables()

                # state
                is_dispenser_homed = global_variables[GlobalVars.DISPENSER_HOMED] == 1
                is_sw_homed = global_variables[GlobalVars.SW_HOMED] == 1
                is_running = global_variables[GlobalVars.RUN] == 1
                pots_dispensed = global_variables[GlobalVars.POTS_DISPENSED]
                is_sw_homing = global_variables[GlobalVars.SW_HOMING] == 1

                # action flags
                # is_reposition_nozzle_requested = global_variables[GlobalVars.REQUEST_REPOSITION_NOZZLE] == 1
                # is_raise_nozzle_requested = global_variables[GlobalVars.REQUEST_RAISE_NOZZLE] == 1
                # is_clear_sw_fault_requested = global_variables[GlobalVars.REQUEST_SW_CLEAR_FAULT] == 1
                # is_sw_home_requested = global_variables[GlobalVars.REQUEST_SW_HOME] == 1

                # =================================== Fetch sensors ================================== #
                sensor_readings = components.A2.read_object("sensors.gpIn")

                is_sw_error = sensor_readings[Sensors.SW_ERROR]["value"] == 1
                is_buff_in_triggered = sensor_readings[Sensors.BUFF_IN]["value"] == 1
                is_buff_out_triggered = sensor_readings[Sensors.BUFF_OUT]["value"] == 1
                has_pot = sensor_readings[Sensors.POT_PRESENCE]["value"] == 1

                # =================================== Update Status ================================== #
                with self.__lock_status:
                    self.__status.connected = True
                    self.__status.running = is_running
                    self.__status.dispenser_homed = is_dispenser_homed
                    self.__status.sw_error = is_sw_error
                    self.__status.sw_homed = is_sw_homed
                    self.__status.buff_in = is_buff_in_triggered
                    self.__status.buff_out = is_buff_out_triggered
                    self.__status.pot_sensor = has_pot

                # =================================== Reset Timers? ================================== #
                if not is_buff_in_triggered:
                    buff_in_empty_timer.reset_timer()

                # ======================================= Run? ======================================= #
                if is_sw_homing:
                    self.__update_status_code(StatusCode.SW_HOMING)

                else:
                    if SV.run_1a:
                        if not is_running:
                            self.__update_status_code(StatusCode.STARTING)

                            # reset pots dispensed
                            components.A2.reset_pots_dispensed()

                            # start
                            components.A2.start()

                            # reset timer
                            buff_in_empty_timer.reset_timer()

                            # create new data session
                            data.A2.create_session()

                        else:
                            # log pots dispensed
                            data.A2.update_data(pots_dispensed)

                            if is_sw_error:
                                self.__update_status_code(StatusCode.SW_ERROR)
                            elif not is_dispenser_homed:
                                self.__update_status_code(StatusCode.DISPENSER_NOT_HOMED)
                            elif not is_sw_homed:
                                self.__update_status_code(StatusCode.SW_NOT_HOMED)
                            elif not is_buff_out_triggered:
                                self.__update_status_code(StatusCode.WAITING_BUF_OUT)
                            elif not is_buff_in_triggered:
                                if buff_in_empty_timer.is_overtime:
                                    self.__update_status_code(StatusCode.WAITING_BUF_IN_TIMEOUT)
                                else:
                                    self.__update_status_code(StatusCode.WAITING_BUF_IN)
                            else:
                                self.__update_status_code(StatusCode.DISPENSING)

                    else:
                        if is_running:
                            self.__update_status_code(StatusCode.STOPPING)

                            # stop
                            components.A2.stop()
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
