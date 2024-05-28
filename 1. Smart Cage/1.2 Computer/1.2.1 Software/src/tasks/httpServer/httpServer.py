import http.server
import time
import threading

# ------------------------------------------------------------------------------------------------ #
from src.tasks.httpServer import httpGetHandler, httpPostHandler
from src import CLI
from src.CLI import Level

KILLER = threading.Event()


class httpHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.parsed_url = (self.path).split("/")
        if self.parsed_url[1] in httpGetHandler.GET_LIST:
            func_name = httpGetHandler.generateFuncName(self.parsed_url[1])
            func = getattr(httpGetHandler, func_name, lambda: "Invalid")
            func(self)

    def do_POST(self):
        self.parsed_url = (self.path).split("/")
        if self.parsed_url[1] in httpPostHandler.POST_LIST:
            func_name = httpPostHandler.generateFuncName(self.parsed_url[1])
            func = getattr(httpPostHandler, func_name, lambda: "Invalid")
            func(self)

    def log_message(self, format, *args):
        return


def start_server(stop_event: threading.Event, PORT=8080):
    with http.server.HTTPServer(("", PORT), httpHandler) as httpd:
        CLI.printline(Level.INFO, f"(HTTP_Server)-Serving at port {PORT}")
        while not stop_event.is_set():
            httpd.handle_request()
        CLI.printline(Level.ERROR, "(HTTP_Server)-Server Stop")


def create_thread():
    global KILLER
    return threading.Thread(target=start_server, args=(KILLER,))


# ################################################################################################ #
#                                              Example                                             #
# ################################################################################################ #
if __name__ == "__main__":
    # Create http server Thread
    stopEvent_http_server = threading.Event()
    thread_server = threading.Thread(target=start_server, args=(stopEvent_http_server,))
    thread_server.start()

    # Main Loop
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            stopEvent_http_server.set()  # Set the stop event
            print("[ INFO ] - httpServer ThreadStop")
            thread_server.join()
            break
