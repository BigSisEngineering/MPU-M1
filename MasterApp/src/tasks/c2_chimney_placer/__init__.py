import threading

from src import components
from src.components.c2_chimney_placer import Status, Sensors
from src._shared_variables import SV
from src.utils import WarningTimer

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "CHIMNEY_PLACER"


class StatusCode:
    IDLE = 0
    OFFLINE = 1
    CAPPING = 2
    WAITING_FOR_CHIMNEY = 3
    WAITING_FOR_CHIMNEY_TIMEOUT = 4
    WAITING_FOR_POT = 5
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
        no_chimney_timer = WarningTimer(30)

        while True:
            try:
                # =================================== Fetch sensors ================================== #
                sensor_readings = components.C2.read_object("sensors.gpIn")

                is_pot_present = sensor_readings[Sensors.POT_PRESENCE]["value"] == 1
                is_chimney_present = sensor_readings[Sensors.CHIMNEY_PRESENCE]["value"] == 1

                # =================================== Fetch Status =================================== #
                is_running = not components.C2.is_idle

                # =================================== Update Status ================================== #
                with self.__lock_status:
                    self.__status.connected = True
                    self.__status.running = is_running
                    self.__status.pot_sensor = is_pot_present
                    self.__status.chimney_sensor = is_chimney_present

                # =================================== Reset Timer? =================================== #
                if is_chimney_present:
                    no_chimney_timer.reset_timer()

                # ======================================= Run? ======================================= #
                if SV.run_1c:
                    if not is_running:
                        self.__update_status_code(StatusCode.STARTING)
                        no_chimney_timer.reset_timer()
                        components.C2.start()
                    else:
                        if not is_chimney_present:
                            if no_chimney_timer.is_overtime:
                                self.__update_status_code(StatusCode.WAITING_FOR_CHIMNEY_TIMEOUT)
                            else:
                                self.__update_status_code(StatusCode.WAITING_FOR_CHIMNEY)
                        elif not is_pot_present:
                            self.__update_status_code(StatusCode.WAITING_FOR_POT)
                        else:
                            self.__update_status_code(StatusCode.CAPPING)

                else:
                    if is_running:
                        self.__update_status_code(StatusCode.STOPPING)
                        components.C2.stop()
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
