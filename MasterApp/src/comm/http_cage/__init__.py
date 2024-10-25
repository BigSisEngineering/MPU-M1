import requests
import json
import threading
import time
from typing import Optional, Dict
from requests.exceptions import ConnectionError

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "HTTPCage"

# ------------------------------------------------------------------------------------ #
hide_exception = True

USERNAME = "linaro"
PASSWORD = "linaro"

ACTION_LIST = [
    "STAR_WHEEL_INIT",
    "UNLOADER_INIT",
    "ALL_SERVOS_INIT",
    "CLEAR_STAR_WHEEL_ERROR",
    "CLEAR_UNLOADER_ERROR",
    "ENABLE_DUMMY",
    "DISABLE_DUMMY",
    "ENABLE_PNP",
    "DISABLE_PNP",
    "ENABLE_EXPERIMENT",
    "DISABLE_EXPERIMENT",
    "MOVE_CW",
    "MOVE_CCW",
    "SET_PAUSE_INTERVAL",
]


class HTTPCage:
    lock_acquire_timeout_status = 1
    lock_acquire_timeout_action = 5
    request_timeout = (10, 5)
    MAX_TIMEOUT = 3  # instances

    def __init__(self, hostname: str):
        self._cage_ip: Optional[str] = None
        self._hostname = hostname

        # -------------------------------------------------------- #
        self._previous_pot_num = 0
        self._pot_num_thresh = 13
        self._lock_request = threading.Lock()

        # -------------------------------------------------------- #
        self._status = None
        self._timeout_counter: int = 0

    # !glen experiment. To be tidied up
    @staticmethod
    def __get_experiment_iteration(hostname):
        num = 0
        if hostname == "cage0x0001":
            num = 0
        if hostname == "cage0x0002":
            num = 1
        if hostname == "cage0x0003":
            num = 2
        if hostname == "cage0x0004":
            num = 3
        if hostname == "cage0x0005":
            num = 4
        if hostname == "cage0x0006":
            num = 0
        if hostname == "cage0x0007":
            num = 1
        if hostname == "cage0x0008":
            num = 2
        if hostname == "cage0x0009":
            num = 3
        if hostname == "cage0x0010":
            num = 4
        if hostname == "cage0x0011":
            num = 0
        if hostname == "cage0x0012":
            num = 1
        if hostname == "cage0x0013":
            num = 2
        if hostname == "cage0x0014":
            num = 3
        return num

    # PUBLIC
    # -------------------------------------------------------- #
    @property
    def status(self) -> Dict:
        if self._lock_request.acquire(timeout=HTTPCage.lock_acquire_timeout_status):
            try:
                response = requests.get(
                    url=f"http://{self._hostname}.local:8080/BoardData",
                    timeout=HTTPCage.request_timeout,
                )
                self._status = json.loads(response.text)
                self._timeout_counter = 0
                return self._status

            # ?Why
            except ConnectionError as ce:
                if "NewConnectionError" in str(ce.args[0]):
                    # return old status if timeout
                    self._timeout_counter += 1

                    if self._timeout_counter >= HTTPCage.MAX_TIMEOUT:
                        return None

                    return self._status

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) [{:^10}] Exception -> {}".format(print_name, "GET STS", self._hostname, e),
                    )

            finally:
                self._lock_request.release()

        else:
            if not hide_exception:
                CLI.printline(
                    Level.WARNING,
                    "({:^10})-({:^8}) [{:^10}] Failed to acquire request lock!".format(
                        print_name, "GET STS", self._hostname
                    ),
                )
            return self._status
        return None

    def fetch_pot_data(self) -> int:
        if self._lock_request.acquire(timeout=HTTPCage.lock_acquire_timeout_action):
            try:
                pot_num = requests.get(
                    url=f"http://{self._hostname}.local:8080/potData",
                    timeout=HTTPCage.request_timeout,
                ).json()

                if isinstance(pot_num, int):
                    CLI.printline(
                        Level.DEBUG,
                        "({:^10})-({:^8}) [{:^10}] {:^3} pots.".format(print_name, "POTDATA", self._hostname, pot_num),
                    )
                    return pot_num
                else:
                    CLI.printline(
                        Level.WARNING,
                        "({:^10})-({:^8}) [{:^10}] {:^3}".format(print_name, "POTDATA", self._hostname, pot_num),
                    )

            except ConnectionError as ce:
                if "NewConnectionError" in str(ce.args[0]):
                    CLI.printline(
                        Level.WARNING,
                        "({:^10})-({:^8}) [{:^10}] Lost of pots!".format(print_name, "GET STS", self._hostname),
                    )

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) [{:^10}] Exception -> {}".format(print_name, "POTDATA", self._hostname, e),
                    )

            finally:
                self._lock_request.release()

        else:
            if not hide_exception:
                CLI.printline(
                    Level.WARNING,
                    "({:^10})-({:^8}) [{:^10}] Failed to acquire request lock!".format(
                        print_name, "POTDATA", self._hostname
                    ),
                )
        return 0

    def exec_action(self, action, params=None) -> str:
        with self._lock_request:
            try:
                if action in ACTION_LIST:
                    url = f"http://{self._hostname}.local:8080/{action}"

                    # ------------------------------------------------------------------------------------ #
                    # !glen experiment temp
                    if action == "ENABLE_EXPERIMENT":
                        url = url + f"/{HTTPCage.__get_experiment_iteration(self._hostname)}"
                        print(f"url: {url}")
                    # ------------------------------------------------------------------------------------ #

                    if params is not None:
                        params = (params,) if not isinstance(params, tuple) else params
                        for param in params:
                            url = url + f"/{param}"

                    headers = {"Content-Type": "application/json"}
                    response = requests.post(
                        url,
                        headers=headers,
                        json={},
                        timeout=HTTPCage.request_timeout,
                    )

                    CLI.printline(
                        Level.INFO,
                        "({:^10})-({:^8}) [{:^10}] {}".format(
                            print_name, action, self._hostname, response.content.decode("utf-8")
                        ),
                    )
                    return "Successful"

                else:
                    CLI.printline(
                        Level.WARNING,
                        "({:^10})-({:^8}) [{:^10}] Invalid action.".format(print_name, action, self._hostname),
                    )
                    return f"Invalid action."

            except ConnectionError as ce:
                if "NewConnectionError" in str(ce.args[0]):
                    return f"Successful (No response)"

                return f"Successful?"

            except Exception as e:
                CLI.printline(
                    Level.WARNING,
                    "({:^10})-({:^8}) [{:^10}] Error: {}".format(print_name, action, self._hostname, e),
                )
                return f"An error occured"
