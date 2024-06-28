from datetime import datetime
import requests
import json
from src import setup
from typing import Optional

url = "http://18.135.115.43/api/api/cage/egg_count/"


class EggCounter:
    def __init__(self):
        self.cage = setup.CAGE_ID
        # self.cage = 'cage0x0001'
        self.url = url
        self.row_name = setup.ROW_NUMBER
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.timeout = 2  # Timeout set to 1 second
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.start_date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.count = {
            "egg": 0,
            "noegg": 0,
            "max_id": 0,
            "date": self.date,
            "start_time": self.start_date_time,
            "end_time": self.start_date_time,
        }
        print(f"Initializing EggCounter at {self.start_date_time}")
        self.data_init()

    def post_api_data(self, data):
        try:
            response = self.session.post(self.url, data=json.dumps(data), timeout=self.timeout)
            return response
        except requests.exceptions.Timeout:
            print("Request timed out in post_api_data")
        except requests.exceptions.ConnectionError:
            print("Connection error in post_api_data")
        except Exception as e:
            print(f"Unexpected error in post_api_data: {e}")
        return None

    def update_entry(self):
        data = {
            "cage_id": self.cage,
            "egg_pot_count": self.count["egg"],
            "no_egg_pot_count": self.count["noegg"],
            "row": self.row_name,
            "col": "col3c",
            "start_time": self.count["start_time"],
            "end_time": self.count["end_time"],
        }
        return self.post_api_data(data)

    def data_init(self):
        try:
            response = self.update_entry()
            if response and response.status_code == 201:
                response_data = response.json()
                inserted_id = response_data.get("id", None)
                if inserted_id:
                    print(f"Document inserted with id: {inserted_id}")
                    self.count["max_id"] = inserted_id
                else:
                    print("Failed to retrieve the _id from the server response.")
            else:
                print(f"Failed to insert data. Status code: {response.status_code}, Response: {response.text}")

        except Exception as e:
            print(f"Initialization error: {e}")

    def data_update(self, prediction):
        try:
            self.count["end_time"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            if datetime.now().strftime("%Y-%m-%d") == self.count["date"]:
                self.count[prediction] += 1
            else:
                self.date = datetime.now().strftime("%Y-%m-%d")
                self.start_date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
                self.count = {
                    "egg": 0,
                    "noegg": 0,
                    "max_id": 0,
                    "date": self.date,
                    "start_time": self.start_date_time,
                    "end_time": self.start_date_time,
                }
                self.data_init()

        except Exception as e:
            print(f"Update data error in data update: {e}")
            pass

    def data_upload(self):
        try:
            data = {
                "cage_id": self.cage,
                "egg_pot_count": self.count["egg"],
                "no_egg_pot_count": self.count["noegg"],
                "row": self.row_name,
                "col": "col3c",
                "start_time": self.count["start_time"],
                "end_time": self.count["end_time"],
            }
            response = self.session.put(
                self.url + str(self.count["max_id"]) + "/", data=json.dumps(data), timeout=self.timeout
            )
            if response and response.status_code == 200:
                print("Data successfully uploaded.")
            else:
                print(
                    f"Failed to upload data. Status code: {response.status_code if response else 'No response'}, Response: {response.text if response else 'No response'}"
                )
        except requests.exceptions.Timeout as e:
            print(f"Request timed out in data upload {e}")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error in data upload {e}")
        except Exception as e:
            print(f"Upload data error: {e}")



# DataBase = EggCounter()
DataBase: Optional[EggCounter] = None
