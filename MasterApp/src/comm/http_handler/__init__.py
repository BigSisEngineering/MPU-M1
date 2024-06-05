import threading
import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
import time
from typing import List


# ------------------------------------------------------------------------------------------------ #
from src import setup
from src import tasks
from src._shared_variables import SV, Cages
from src import components


DIRECTORY = os.path.join(os.path.dirname(__file__),"..", "front_end")
JSON_FILE_PATH = os.path.join(DIRECTORY, "static", "js", "cage_status.json")


class HttpRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        # self.start_monitoring()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.path = "/template/index.html"
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/1A_1C":
            self.handle_1A_1C()

        elif self.path == "/1B":
            self.execute_cages_action()
        else:
            self.send_error(404, "File not found.")

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

        if data.get("raiseNozzle", False):
            components.A2.raise_nozzle()
        if data.get("lowerNozzle", False):
            components.A2.reposition_nozzle()
        if data.get("clearErrorSW2", False):
            components.A2.sw_ack_fault()
        if data.get("homeSW2", False):
            components.A2.sw_home()
        
        if data.get("clearErrorSW3", False):
            components.A3.sw_ack_fault()
        if data.get("homeSW3", False):
            components.A3.sw_home()

        # Reset toggles immediately after processing
        data["addTen"] = False
        data["setZero"] = False

        data["raiseNozzle"] = False
        data["lowerNozzle"] = False
        data["clearErrorSW2"] = False
        data["homeSW2"] = False

        data["clearErrorSW3"] = False
        data["homeSW3"] = False

        # Send a response back to the client
        self.send_response(200)
        self.end_headers()
        response = {"status": "success"}
        self.wfile.write(json.dumps(response).encode("utf-8"))

    def execute_cages_action(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(post_data)
        print("Received data for execution:", data)

        results = self.get_cages_action(data.get("cages", []), data.get("action", ""))
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(results).encode("utf-8"))

    def get_cages_action(self, cages: List, action: str):
        for cage_id in cages:
            for cage in Cages:
                if cage_id == cage.value:
                    threading.Thread(target=components.cage_dict[cage].exec_action, args=(action,)).start()
                    
    def monitor_variables_1a_1c(self):
        while True:
            # print(f"Current States -> is1AActive: {SV.is1AActive}, is1CActive: {SV.is1CActive}")
            SV.w_run_1a(SV.is1AActive)
            SV.w_run_1c(SV.is1CActive)
            time.sleep(3.5)
    
    def start_monitoring(self):
        self.monitoring_thread = threading.Thread(target=self.monitor_variables_1a_1c)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        



def variables_1a_1c():
    while True:
        # print(f"Current States -> is1AActive: {SV.is1AActive}, is1CActive: {SV.is1CActive}")
        SV.w_run_1a(SV.is1AActive)
        SV.w_run_1c(SV.is1CActive)
        time.sleep(3.5)


def start_http_server():
    # tasks.start()
    port = int(setup.MASTER_SERVER_PORT)
    server_address = ("", port)
    httpd = HTTPServer(server_address, HttpRequestHandler)
    print(f"Starting httpd server on {port}")
    httpd.serve_forever()