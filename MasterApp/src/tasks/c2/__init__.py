import threading

from src import components
from src.components.c2_chimney_placer import Status, Sensors
from src._shared_variables import SV

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "CHIMNEY_PLACER"


class Task:
    def __init__(self):
        self.__lock_status = threading.Lock()
        self.__status: Status = Status()

        self.loop_thread = threading.Thread(target=self.__loop, daemon=True)

    @property
    def status(self):
        with self.__lock_status:
            r = self.__status
        return r.dict()

    def __loop(self):
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

                # ======================================= Run? ======================================= #
                if SV.run_1c:
                    if not is_running:
                        components.C2.start()
                else:
                    if is_running:
                        components.C2.stop()

            except Exception as e:
                # default value
                with self.__lock_status:
                    self.__status = Status()

                CLI.printline(Level.ERROR, "({:^10}) {}".format(print_name, e))

    # -------------------------------------------------------- #
    def start(self):
        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))
        self.loop_thread.start()
