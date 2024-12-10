import requests
import threading
from typing import Optional, Tuple, Any, Union

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "HTTPDuet"
hide_exception = True


class HTTPDuet:
    def __init__(self, duet_ip: str) -> None:
        self._duet_ip = duet_ip
        self._timeout = 1  # seconds

        # ------------------------------------------------------------------------------------ #
        self._lock_request = threading.Lock()

    # ------------------------------------------------------------------------------------ #
    @property
    def is_connected(self) -> bool:
        with self._lock_request:
            try:
                requests.get(url=f"http://{self._duet_ip}/", timeout=self._timeout)
                return True

            except Exception as e:
                if not hide_exception:
                    CLI.printline(Level.ERROR, "({:^10})-({:^8}) Exception -> {}".format(print_name, "CONN", e))
        return False

    @property
    def is_idle(self) -> bool:
        with self._lock_request:
            try:
                status = requests.get(
                    url=f"http://{self._duet_ip}/rr_status?type=3",
                    timeout=self._timeout,
                ).json()

                if status["status"] == "I":
                    return True

            except Exception as e:
                if not hide_exception:
                    CLI.printline(Level.ERROR, "({:^10})-({:^8}) Exception -> {}".format(print_name, "IS_IDLE", e))
        return False

    def run_macro(self, macro_name: str, param: str = None) -> bool:
        with self._lock_request:
            try:
                requests.get(
                    url=f'http://{self._duet_ip}/rr_gcode?gcode=M98 P"0:/macros/{macro_name}" {param}',
                    timeout=self._timeout,
                )
                return True

            except Exception as e:
                if not hide_exception:
                    CLI.printline(Level.ERROR, "({:^10})-({:^8}) Exception -> {}".format(print_name, "RUN_MCR", e))
        return False

    def run_command(self, command_name: str) -> bool:
        with self._lock_request:
            try:
                requests.get(
                    url=f"http://{self._duet_ip}/rr_gcode?gcode={command_name}",
                    timeout=self._timeout,
                )
                return True

            except Exception as e:
                if not hide_exception:
                    CLI.printline(Level.ERROR, "({:^10})-({:^8}) Exception -> {}".format(print_name, "RUN_CMD", e))
        return False

    def fetch_global_variables(self) -> Optional[Union[Tuple, int]]:
        with self._lock_request:
            try:
                global_vars = requests.get(
                    url=f"http://{self._duet_ip}/rr_model?key=global",
                    timeout=self._timeout,
                ).json()["result"]

                return global_vars

            except Exception as e:
                if not hide_exception:
                    CLI.printline(Level.ERROR, "({:^10})-({:^8}) Exception -> {}".format(print_name, "READ_GLB", e))
        return None

    def set_global(self, var_name: str, value: int) -> bool:
        with self._lock_request:
            try:
                requests.get(
                    url=f"http://{self._duet_ip}/rr_gcode?gcode=set global.{var_name}={value}",
                    timeout=self._timeout,
                )
                return True

            except Exception as e:
                if not hide_exception:
                    CLI.printline(Level.ERROR, "({:^10})-({:^8}) Exception -> {}".format(print_name, "SET_GLB", e))
        return False

    def read_object(self, obj_name: str) -> Optional[Any]:
        with self._lock_request:
            try:
                result = requests.get(
                    url=f"http://{self._duet_ip}/rr_model?key={obj_name}",
                    timeout=self._timeout,
                ).json()["result"]
                return result

            except Exception as e:
                if not hide_exception:
                    CLI.printline(Level.ERROR, "({:^10})-({:^8}) Exception -> {}".format(print_name, "READ_OBJ", e))
        return None

    def abort(self) -> None:
        with self._lock_request:
            try:
                requests.get(
                    f"http://{self._duet_ip}/rr_gcode?gcode=M112 M999",
                    timeout=self._timeout,
                )

            except Exception as e:
                if not hide_exception:
                    CLI.printline(Level.ERROR, "({:^10})-({:^8}) Exception -> {}".format(print_name, "ABORT", e))


# ------------------------------------------------------------------------------------ #
def debug():
    obj = HTTPDuet("10.207.13.11")

    print(obj.is_connected)
    print(obj.is_idle)
    print(obj.run_macro("ring_light_intensity.g", "A255"))
    print(obj.run_command("M42 P0 S0"))
    print(obj.fetch_global_variables("cycle_time"))
    print(obj.read_object("sensors.gpIn[0].value"))
    print(obj.abort())
