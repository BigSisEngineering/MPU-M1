import threading

from src import components
from src.components.c1_chimney_sorter import Status, Sensors
from src._shared_variables import SV
from src.utils import WarningTimer

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "CHIMNEY_SORTER"


class StatusCode:
    IDLE = 0
    OFFLINE = 1
    SORTING = 2
    SORTING_TIMEOUT = 3
    WAITING_BUF_OUT = 4
    WAITING_BUF_OUT_TIMEOUT = 5
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
        buff_out_full_timer = WarningTimer(30)
        buff_out_empty_timer = WarningTimer(30)

        while True:
            try:
                # =================================== Fetch sensors ================================== #
                sensor_readings = components.C1.read_object("sensors.gpIn")

                is_output_buffer_triggered = sensor_readings[Sensors.BUFF_OUT]["value"] == 1
                is_channel_1_buffer_triggered = sensor_readings[Sensors.CHANNEL_1_BUFFER]["value"] == 1
                is_channel_2_buffer_triggered = sensor_readings[Sensors.CHANNEL_2_BUFFER]["value"] == 1
                is_channel_3_buffer_triggered = sensor_readings[Sensors.CHANNEL_3_BUFFER]["value"] == 1

                # =================================== Fetch Status =================================== #
                is_running = not components.C1.is_idle

                # =================================== Update Status ================================== #
                with self.__lock_status:
                    self.__status.connected = True
                    self.__status.running = is_running
                    self.__status.buff_out = is_output_buffer_triggered
                    self.__status.chn1_sensor = is_channel_1_buffer_triggered
                    self.__status.chn2_sensor = is_channel_2_buffer_triggered
                    self.__status.chn3_sensor = is_channel_3_buffer_triggered

                # =================================== Reset Timer? =================================== #
                if is_output_buffer_triggered:  # if no chimney at buffer
                    buff_out_full_timer.reset_timer()  # reset full
                else:
                    buff_out_empty_timer.reset_timer()  # reset empty

                # ======================================= Run? ======================================= #
                if SV.run_1c:
                    if not is_running:
                        self.__update_status_code(StatusCode.STARTING)
                        buff_out_full_timer.reset_timer()
                        buff_out_empty_timer.reset_timer()
                        components.C1.start()
                    else:
                        if is_output_buffer_triggered:  # if no chimney at buffer, sort
                            if buff_out_empty_timer.is_overtime:  # is empty for too long?
                                self.__update_status_code(StatusCode.SORTING_TIMEOUT)
                            else:
                                self.__update_status_code(StatusCode.SORTING)
                        else:
                            if buff_out_full_timer.is_overtime:  # is full for too long?
                                self.__update_status_code(StatusCode.WAITING_BUF_OUT_TIMEOUT)
                            else:
                                self.__update_status_code(StatusCode.WAITING_BUF_OUT)

                else:
                    if is_running:
                        self.__update_status_code(StatusCode.STOPPING)
                        components.C1.stop()
                    else:
                        self.__update_status_code(StatusCode.IDLE)

            except Exception as e:
                # default value
                with self.__lock_status:
                    self.__status = Status()

                self.__update_status_code(StatusCode.OFFLINE)

                CLI.printline(Level.ERROR, "({:^10}) {}".format(print_name, e))

    # -------------------------------------------------------- #
    def start(self):
        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))
        self.loop_thread.start()
