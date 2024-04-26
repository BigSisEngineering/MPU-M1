import threading
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import os

# ------------------------------------------------------------------------------------------------ #
# from src import tasks, components

# -------------------------------------------------------- #
# from src._shared_variables import SV, Cages


# main2.py

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

# The DIRECTORY variable should point to the 'frontEnd' folder
DIRECTORY = os.path.join(os.path.dirname(__file__), 'src', 'frontEnd')

class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Serve template/index.html when the root is accessed
        if self.path == '/':
            self.path = '/template/index.html'
        return SimpleHTTPRequestHandler.do_GET(self)

def run(server_class=HTTPServer, handler_class=MyHttpRequestHandler):
    port = 8080
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()


