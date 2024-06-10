import requests
import json
import threading
import paramiko
import time
from typing import Optional, Dict

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "HTTPGate"

# -------------------------------------------------------- #
from src._shared_variables import SV

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
    "MOVE_CW",
    "MOVE_CCW",
]


class HTTPCage:
    def __init__(self, hostname: str):
        self._cage_ip: Optional[str] = None
        self._hostname = hostname
        self._timeout = 5  # seconds

        # -------------------------------------------------------- #
        self._previous_pot_num = 0
        self._pot_num_thresh = 13
        self._lock_request = threading.Lock()

        # -------------------------------------------------------- #
        threading.Thread(target=self._find_ip_from_hostname).start()

    # PRIVATE
    # -------------------------------------------------------- #
    def _find_ip_from_hostname(self) -> None:

        with self._lock_request:
            CLI.printline(
                Level.INFO,
                "({:^10})-({:^8}) [{:^10}] -> Start".format(print_name, "FIND IP", self._hostname),
            )

            time_stamp = time.time()
            interval = 5  # seconds

            while not SV.KILLER_EVENT.is_set() and self._cage_ip is None:
                if (time.time() - time_stamp) > interval:
                    try:
                        # Create an SSH client
                        ssh_client = paramiko.SSHClient()
                        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                        # Connect to the remote device
                        ssh_client.connect(
                            self._hostname + ".local",
                            username=USERNAME,
                            password=PASSWORD,
                        )

                        # Run the 'ip addr show eth0' command to get information about the eth0 interface
                        stdin, stdout, stderr = ssh_client.exec_command("ip addr show eth0")

                        # Read the output and extract the IP address
                        output = stdout.read().decode()
                        lines = output.split("\n")
                        for line in lines:
                            if "inet " in line:  # Look for the line containing 'inet ' (IPv4 address)
                                ip_address = line.split()[1].split("/")[0]

                                CLI.printline(
                                    Level.INFO,
                                    "({:^10})-({:^8}) [{:^10}] -> {}".format(
                                        print_name,
                                        "FIND IP",
                                        self._hostname,
                                        ip_address,
                                    ),
                                )

                                self._cage_ip = ip_address

                                # Close the SSH connection
                                ssh_client.close()

                        ssh_client.close()

                    except Exception as e:
                        if not hide_exception:
                            CLI.printline(
                                Level.ERROR,
                                "({:^10})-({:^8}) [{:^10}] Exception -> {}".format(
                                    print_name, "FIND IP", self._hostname, e
                                ),
                            )

                    if self._hostname is None:
                        CLI.printline(
                            Level.WARNING,
                            "({:^10})-({:^8}) IP for {} not found! Retrying in 5s...".format(
                                print_name, "FIND IP", self._hostname
                            ),
                        )
                        time_stamp = time.time()

        CLI.printline(
            Level.DEBUG,
            "({:^10})-({:^8}) [{:^10}] -> Stop".format(print_name, "FIND IP", self._hostname),
        )

    # PUBLIC
    # -------------------------------------------------------- #
    @property
    def status(self) -> Optional[Dict]:
        if self._lock_request.acquire(timeout=1):
            try:
                response = requests.get(
                    url=f"http://{self._cage_ip}:8080/BoardData",
                    timeout=self._timeout,
                )
                return json.loads(response.text)

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
        return None

    def execute_action(self, action_name: str) -> None:
        if action_name == "RESTART":
            return self.restart_software()
        else:
            try:
                requests.post(
                    url=f"http://{self._cage_ip}:8080/{action_name}",
                    timeout=1,
                )
                CLI.printline(
                    Level.INFO,
                    "({:^10})-({:^8}) [{:^10}] Execute -> {}".format(print_name, "EXEC", self._hostname, action_name),
                )
            except:
                CLI.printline(
                    Level.ERROR,
                    "({:^10})-({:^8}) [{:^10}] Execute -> {} Failed!".format(
                        print_name, "EXEC", self._hostname, action_name
                    ),
                )

    def restart_software(self) -> None:
        if self._lock_request.acquire(timeout=self._timeout):
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                ssh_client.connect(
                    self._cage_ip + ".local",
                    username=USERNAME,
                    password=PASSWORD,
                )

                stdin, stdout, stderr = ssh_client.exec_command("ip addr show eth0")

                output = stdout.read().decode()
                CLI.printline(
                    Level.INFO,
                    "({:^10})-({:^8}) [{:^10}] Execute -> {}".format(
                        print_name, "EXEC", self._hostname, "RESTART SOFTWARE"
                    ),
                )

            except:
                CLI.printline(
                    Level.ERROR,
                    "({:^10})-({:^8}) [{:^10}] Execute -> {} Failed!".format(
                        print_name, "EXEC", self._hostname, "RESTART SOFTWARE"
                    ),
                )
            finally:
                self._lock_request.release()

    def fetch_pot_data(self) -> int:
        if self._lock_request.acquire(timeout=self._timeout):
            try:
                pot_num = requests.get(
                    url=f"http://{self._cage_ip}:8080/potData",
                    timeout=1,
                ).json()

                if isinstance(pot_num, int):
                    CLI.printline(
                        Level.DEBUG,
                        "({:^10})-({:^8}) [{:^10}] {:^3} pots.".format(print_name, "POTDATA", self._hostname, pot_num),
                    )
                    self._previous_pot_num = pot_num
                    if pot_num > self._pot_num_thresh and self._previous_pot_num > self._pot_num_thresh:
                        CLI.printline(
                            Level.WARNING,
                            "({:^10})-({:^8}) [{:^10}] Requested more than {} pots twice! Check infeed channel!".format(
                                print_name, "POTDATA", self._hostname, pot_num
                            ),
                        )
                        pot_num = 0

                    return pot_num

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

    def exec_action(self, action) -> None:
        if self._lock_request.acquire(timeout=self._timeout):
            try:
                if action in ACTION_LIST:
                    url = f"http://{self._cage_ip}:8080/{action}"
                    headers = {"Content-Type": "application/json"}
                    response = requests.post(url, headers=headers, json={}, timeout=5)

                    if response is not None:
                        CLI.printline(
                            Level.INFO,
                            "({:^10})-({:^8}) [{:^10}] {}".format(
                                print_name, action, self._hostname, response.content.decode("utf-8")
                            ),
                        )
                    else:
                        CLI.printline(
                            Level.INFO,
                            "({:^10})-({:^8}) [{:^10}] No response.".format(print_name, action, self._hostname),
                        )
                else:
                    CLI.printline(
                        Level.WARNING,
                        "({:^10})-({:^8}) [{:^10}] Invalid action.".format(print_name, action, self._hostname),
                    )
            except Exception as e:
                CLI.printline(
                    Level.WARNING,
                    "({:^10})-({:^8}) [{:^10}] Error: {}".format(print_name, action, self._hostname, e),
                )

            finally:
                self._lock_request.release()

        else:
            # if not hide_exception:
            CLI.printline(
                Level.WARNING,
                "({:^10})-({:^8}) [{:^10}] Failed to acquire request lock!".format(print_name, action, self._hostname),
            )
