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

        # ------------------------------------------------------------------------------------ #
        self.lock_data = threading.Lock()
        self.data = {
            "diet_dispenser_id": setup.ROW,
            "no_of_pots_dispensed": 0,
            "start_time": "2023-04-19T10:39:50.341814Z",
            "end_time": "2023-04-19T10:39:50.341814Z",
        }

        # ------------------------------------------------------------------------------------ #
        self.lock_PUT = threading.Lock()

    def _get_current_time(self) -> str:
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    def _PUT(self):
        if self.lock_PUT.acquire(timeout=1):
            payload = json.dumps(self.data)
            headers = {"Content-Type": "application/json"}

            response = requests.request("PUT", self.url, headers=headers, data=payload)

            CLI.printline(Level.INFO, "({:^10}) PUT -> {}".format(print_name, response.text))

            self.lock_PUT.release()
        else:
            CLI.printline(Level.WARNING, "({:^10}) PUT not executed.".format(print_name))

    def _update_data_thread(self, num_pots) -> None:
        with self.lock_data:
            self.data["no_of_pots_dispensed"] += num_pots
            self.data["end_time"] = self._get_current_time()
            self._PUT()

    # ------------------------------------------------------------------------------------ #
    def create_session(self) -> None:
        with self.lock_data:
            self.data["no_of_pots_dispensed"] = 0
            self.data["start_time"] = self._get_current_time()
            self.data["end_time"] = self._get_current_time()
            self._PUT()

    def update_data(self, num_pots) -> None:
        threading.Thread(target=self._update_data_thread, args=(num_pots,)).start()
