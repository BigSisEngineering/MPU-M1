import requests
import json
import threading
from datetime import datetime

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "A2 Data"

# ------------------------------------------------------------------------------------ #
from src import setup


class Data:
    def __init__(self):
        self.url = "http://18.135.115.43/api/api/diet_dispense/diet/"
        self.session_key = None

        # ------------------------------------------------------------------------------------ #
        self.lock_data = threading.Lock()
        self.data = {
            "diet_dispenser_id": setup.ROW,
            "no_of_pots_dispensed": 0,
            "start_time": "2023-04-19T10:39:50.341814Z",
            "end_time": "2023-04-19T10:39:50.341814Z",
        }

        # ------------------------------------------------------------------------------------ #
        self.lock_upload = threading.Lock()

    def _get_current_time(self) -> str:
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    def _POST(self) -> None:
        if self.lock_upload.acquire(timeout=1):
            try:
                payload = json.dumps(self.data)
                headers = {"Content-Type": "application/json"}

                url = self.url
                response = requests.request("POST", url, headers=headers, data=payload)
                self.session_key = response.json().get("id", None)

                CLI.printline(Level.INFO, "({:^10}) POST -> {}".format(print_name, self.session_key))

            except Exception as e:
                CLI.printline(Level.ERROR, "({:^10}) POST ERROR-> {}".format(print_name, e))

            self.lock_upload.release()

            return
        CLI.printline(Level.WARNING, "({:^10}) POST not executed.".format(print_name))

    def _PUT(self) -> None:
        if self.lock_upload.acquire(timeout=1):
            try:
                payload = json.dumps(self.data)
                headers = {"Content-Type": "application/json"}

                if self.session_key is not None:
                    url = "{}{}/".format(self.url, self.session_key)

                    requests.request("PUT", url, headers=headers, data=payload, timeout=2)

                    CLI.printline(Level.INFO, "({:^10}) PUT -> {}".format(print_name, self.session_key))
                    self.lock_upload.release()
                    return
                else:
                    CLI.printline(Level.WARNING, "({:^10}) Attempting to repost session".format(print_name))
                    self.lock_upload.release()
                    self._POST()
                    return

            except Exception as e:
                CLI.printline(Level.ERROR, "({:^10}) PUT ERROR-> {}".format(print_name, e))

            self.lock_upload.release()

        CLI.printline(Level.WARNING, "({:^10}) POST not executed.".format(print_name))

    def _update_data_thread(self, num_pots) -> None:
        with self.lock_data:
            self.data["no_of_pots_dispensed"] = num_pots
            self.data["end_time"] = self._get_current_time()
            self._PUT()

    # ------------------------------------------------------------------------------------ #
    def create_session(self) -> None:
        with self.lock_data:
            self.data["no_of_pots_dispensed"] = 0
            self.data["start_time"] = self._get_current_time()
            self.data["end_time"] = self._get_current_time()
            self._POST()

    def update_data(self, num_pots) -> None:
        threading.Thread(target=self._update_data_thread, args=(num_pots,)).start()


def debug():
    import time

    obj = Data()
    obj.create_session()

    time.sleep(1)
    obj.update_data(5)

    time.sleep(1)
    obj.update_data(5)
