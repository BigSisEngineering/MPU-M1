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
]


class HTTPCage:
    lock_acquire_timeout_status = 1
    lock_acquire_timeout_action = 5
    request_timeout = (10, 5)

    def __init__(self, hostname: str):
        self._cage_ip: Optional[str] = None
        self._hostname = hostname

        # -------------------------------------------------------- #
        self._previous_pot_num = 0
        self._pot_num_thresh = 13
        self._lock_request = threading.Lock()

        # -------------------------------------------------------- #
        self._status = None

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
                return self._status

            # ?Why
            except ConnectionError as ce:
                if "NewConnectionError" in str(ce.args[0]):
                    # return old status if timeout
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

    def execute_action(self, action_name: str) -> None:
        if self._lock_request.acquire(timeout=HTTPCage.lock_acquire_timeout_action):
            try:
                requests.post(
                    url=f"http://{self._hostname}.local:8080/{action_name}",
                    timeout=HTTPCage.request_timeout,
                )
                CLI.printline(
                    Level.INFO,
                    "({:^10})-({:^8}) [{:^10}] Execute -> {}".format(print_name, "EXEC", self._hostname, action_name),
                )
            except Exception:
                CLI.printline(
                    Level.ERROR,
                    "({:^10})-({:^8}) [{:^10}] Execute -> {} Failed!".format(
                        print_name, "EXEC", self._hostname, action_name
                    ),
                )
            finally:
                self._lock_request.release()

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

    def exec_action(self, action) -> str:
        if self._lock_request.acquire(timeout=HTTPCage.lock_acquire_timeout_action):
            try:
                if action in ACTION_LIST:
                    url = f"http://{self._hostname}.local:8080/{action}"
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
                    # return "{}".format(response.content.decode("utf-8"))
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

            finally:
                self._lock_request.release()

        else:
            CLI.printline(
                Level.WARNING,
                "({:^10})-({:^8}) [{:^10}] Failed to acquire request lock!".format(print_name, action, self._hostname),
            )
            return f"Send failed. Cage is busy."
