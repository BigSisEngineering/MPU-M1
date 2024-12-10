import threading

from src import components
from src.components.a2_diet_dispenser import Status, Sensors, GlobalVars
from src import data
from src._shared_variables import SV

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "DIET_DSP"


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
                # =================================== Fetch global =================================== #
                global_variables = components.A2.fetch_global_variables()

                # state
                is_dispenser_homed = global_variables[GlobalVars.DISPENSER_HOMED] == 1
                is_sw_homed = global_variables[GlobalVars.SW_HOMED] == 1
                is_running = global_variables[GlobalVars.RUN] == 1
                pots_dispensed = global_variables[GlobalVars.POTS_DISPENSED]
                is_sw_homing = global_variables[GlobalVars.SW_HOMING]

                # action flags
                is_reposition_nozzle_requested = global_variables[GlobalVars.REQUEST_REPOSITION_NOZZLE] == 1
                is_raise_nozzle_requested = global_variables[GlobalVars.REQUEST_RAISE_NOZZLE] == 1
                is_clear_sw_fault_requested = global_variables[GlobalVars.REQUEST_SW_CLEAR_FAULT] == 1
                is_sw_home = global_variables[GlobalVars.REQUEST_SW_HOME] == 1

                # =================================== Fetch sensors ================================== #
                sensor_readings = components.A2.read_object("sensors.gpIn")

                is_sw_error = sensor_readings[Sensors.SW_ERROR]["value"] == 1
                is_buff_in_triggered = sensor_readings[Sensors.BUFF_IN]["value"] == 1
                is_buff_out_triggered = sensor_readings[Sensors.BUFF_OUT]["value"] == 1
                has_pot = sensor_readings[Sensors.POT_PRESENCE]["value"] == 1

                # =================================== Update Status ================================== #
                with self.lock_status:
                    self.status.connected = True
                    self.status.running = is_running
                    self.status.dispenser_homed = is_dispenser_homed
                    self.status.sw_error = is_sw_error
                    self.status.sw_homed = is_sw_homed
                    self.status.buff_in = is_buff_in_triggered
                    self.status.buff_out = is_buff_out_triggered
                    self.status.pot_sensor = has_pot

                # ======================================= Run? ======================================= #
                if SV.run_1a:
                    if not is_running and not is_sw_homing:
                        # reset pots dispensed
                        components.A2.reset_pots_dispensed()

                        # start
                        components.A2.start()

                        # create new data session
                        data.A2.create_session()

                    else:
                        # log pots dispensed
                        data.A2.update_data(pots_dispensed)
                else:
                    if is_running and not is_sw_homing:
                        components.A2.stop()

            except Exception as e:
                # default value
                with self.lock_status:
                    self.status = Status()

                CLI.printline(Level.ERROR, "({:^10}) {}".format(print_name, e))

    def start(self):
        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))
        self.loop_thread.start()
