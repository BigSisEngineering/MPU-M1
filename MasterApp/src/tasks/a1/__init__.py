import threading

from src import components
from src.components.a1_pot_sorter import Status, Sensors
from src._shared_variables import SV

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "POT_SORTER"


class Task:
    def __init__(self):
        self.lock_status = threading.Lock()
        self.status: Status = Status()

        self.loop_thread = threading.Thread(target=self.__loop, daemon=True)

    @property
    def status(self):
        with self.lock_status:
            status = self.status
        return status.dict()

    def __loop(self):
        while True:
            try:
                # =================================== Fetch Sensors ================================== #
                sensor_readings = components.A1.read_object("sensors.gpIn")
                is_buff_out_triggered = sensor_readings[Sensors.BUFF_OUT]["value"] == 1

                # =================================== Fetch Status =================================== #
                is_running = not components.A1.is_idle

                # =================================== Update Status ================================== #
                with self.lock_status:
                    self.status.connected = True
                    self.status.running = is_running
                    self.status.buff_out = is_buff_out_triggered

                # ======================================= Run? ======================================= #
                if SV.run_1a:
                    if not is_running:
                        components.A1.start()
                else:
                    if is_running:
                        components.A1.stop()

            except Exception as e:
                # default value
                with self.lock_status:
                    self.status = Status()

                CLI.printline(Level.ERROR, "({:^10}) {}".format(print_name, e))

    def start(self):
        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))
        self.loop_thread.start()
