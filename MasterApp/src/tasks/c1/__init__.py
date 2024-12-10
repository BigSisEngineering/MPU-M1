import threading
import time

from src import components
from src.components.c1_chimney_sorter import Status, Sensors
from src._shared_variables import SV

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "CHIMNEY_SORTER"


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
                sensor_readings = components.C1.read_object("sensors.gpIn")

                is_output_buffer_full = sensor_readings[Sensors.BUFF_OUT]["value"] == 1
                is_channel_1_buffer_triggered = sensor_readings[Sensors.CHANNEL_1_BUFFER]["value"] == 1
                is_channel_2_buffer_triggered = sensor_readings[Sensors.CHANNEL_2_BUFFER]["value"] == 1
                is_channel_3_buffer_triggered = sensor_readings[Sensors.CHANNEL_3_BUFFER]["value"] == 1

                # =================================== Fetch Status =================================== #
                is_running = not components.C1.is_idle

                # =================================== Update Status ================================== #
                with self.__lock_status:
                    self.__status.connected = True
                    self.__status.running = is_running
                    self.__status.buff_out = is_output_buffer_full
                    self.__status.chn1_sensor = is_channel_1_buffer_triggered
                    self.__status.chn2_sensor = is_channel_2_buffer_triggered
                    self.__status.chn3_sensor = is_channel_3_buffer_triggered

                # ======================================= Run? ======================================= #
                if SV.run_1c:
                    if not is_running:
                        components.C1.start()
                else:
                    if is_running:
                        components.C1.stop()

            except Exception as e:
                # default value
                with self.__lock_status:
                    self.__status = Status()

                CLI.printline(Level.ERROR, "({:^10}) {}".format(print_name, e))

    # -------------------------------------------------------- #
    def start(self):
        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))
        self.loop_thread.start()
