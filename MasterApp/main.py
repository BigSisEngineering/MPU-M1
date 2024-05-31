import threading
import os
import json
import urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
import time
import tempfile
import requests


# ------------------------------------------------------------------------------------------------ #
from src import tasks
from src._shared_variables import SV


DIRECTORY = os.path.join(os.path.dirname(__file__), "src", "front_end")
JSON_FILE_PATH = os.path.join(DIRECTORY, "static", "js", "cage_status.json")


class HttpRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/template/index.html"
        # if self.path == "/get_all_cages_status":
        #     self.handle_all_cages_status()
            # return  # Important: Return after handling the request to prevent further processing
        # else:
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/control_1A_1C":
            self.handle_1A_1C()

        elif self.path == "/execute_actions":
            self.handle_execute_actions()
        else:
            self.send_error(404, "File not found.")

    # def handle_all_cages_status(self):
    #     response = get_all_cages_status()
    #     self.send_response(200)
    #     self.send_header("Content-type", "application/json")
    #     self.end_headers()
    #     self.wfile.write(json.dumps(response).encode("utf-8"))

    def handle_1A_1C(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(post_data)

        # Process the received data
        SV.is1AActive = data.get("is1AActive", False)
        SV.is1CActive = data.get("is1CActive", False)

        # Check for toggles and execute associated tasks
        if data.get("addTen", False):
            tasks.a3_task.add_pots(10)
        if data.get("setZero", False):
            tasks.a3_task.set_zero()

        # Reset toggles immediately after processing
        data["addTen"] = False
        data["setZero"] = False

        # Send a response back to the client
        self.send_response(200)
        self.end_headers()
        response = {"status": "success"}
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def handle_execute_actions(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(post_data)
        print("Received data for execution:", data)

        results = self.execute_actions_on_cages(data.get("cages", []), data.get("action", ""))
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(results).encode("utf-8"))

    def execute_actions_on_cages(self, cages, action):
        results = {}
        for cage_id in cages:
            url = f"http://{cage_id}:8080/{action}"
            headers = {"Content-Type": "application/json"}
            try:
                # Assuming POST is the correct method for executing actions
                response = requests.post(url, headers=headers, json={}, timeout=5)
                if response.status_code == 200:
                    response_text = response.content.decode("utf-8")
                    results[cage_id] = {
                        "status": "success",
                        "response": response_text,
                        "status_code": response.status_code,
                    }
                else:
                    results[cage_id] = {
                        "status": "error",
                        "message": f"Failed with status code {response.status_code}",
                        "response": response.text,
                    }
                print(f"Request sent to {url} with headers {headers} received response: {response.text}")
                time.sleep(0.1)
            except requests.exceptions.RequestException as e:
                results[cage_id] = {"status": "error", "message": str(e)}
                print(f"Failed to send request to {url} with headers {headers}")
        return results


# def get_all_cages_status():
#     cage_addresses = [f"cage0x000{i}" for i in range(2, 10)] + [f"cage0x00{i}" for i in range(10, 16)]
#     results = {}
#     with threading.Lock():  # Locking to ensure thread safety for the shared 'results' dictionary
#         threads = []
#         for address in cage_addresses:
#             thread = threading.Thread(target=request_cage_data, args=(address, results))
#             threads.append(thread)
#             thread.start()

#         for thread in threads:
#             thread.join()
#     # Save results to a JSON file
#     with open(JSON_FILE_PATH, "w") as f:
#         json.dump(results, f)

#     # print(f"All cages status : {results}")
#     # for address, data in results.items():
#     #     print(f"{address}: {data}")

#     return results


# def request_cage_data(address, results):
#     url = f"http://{address}:8080/BoardData"
#     try:
#         response = requests.get(url, timeout=5)
#         if response.status_code == 200:
#             results[address] = response.json()
#         else:
#             results[address] = {"error": f"Failed to fetch data with status code {response.status_code}"}
#         print(f"Data for {address}: {results[address]}")  # Print fetched data
#     except requests.exceptions.RequestException as e:
#         results[address] = {"error": str(e)}
#         # print(f"Error fetching data for {address}: {e}")  # Print errors


# def fetch_data_periodically():
#     while True:
#         get_all_cages_status()
#         time.sleep(5)  # Fetch data every 3 seconds, can be adjusted as needed


def variables_1a_1c():
    while True:
        # print(f"Current States -> is1AActive: {SV.is1AActive}, is1CActive: {SV.is1CActive}")
        SV.w_run_1a(SV.is1AActive)
        SV.w_run_1c(SV.is1CActive)
        time.sleep(3)


def run():
    tasks.start()
    port = 8080
    server_address = ("", port)
    httpd = HTTPServer(server_address, HttpRequestHandler)

    # # Start fetching data periodically in a daemon thread
    # data_fetch_thread = threading.Thread(target=fetch_data_periodically)
    # data_fetch_thread.daemon = True
    # data_fetch_thread.start()

    monitoring_thread = threading.Thread(target=variables_1a_1c)
    monitoring_thread.daemon = True
    monitoring_thread.start()

    print(f"Starting httpd server on {port}")
    httpd.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=run).start()

    # ------------------------------------------------------------------------------------ #
    from src import components

    try:
        components.debug()

    except KeyboardInterrupt:
        SV.KILLER_EVENT.set()
