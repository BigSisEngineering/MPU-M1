import http.server
import time
import threading
import os
from urllib.parse import unquote
from http import HTTPStatus

# ------------------------------------------------------------------------------------------------ #
from src.tasks.httpServer import httpGetHandler, httpPostHandler
from src import CLI
from src.CLI import Level

KILLER = threading.Event()


class httpHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.parsed_url = (self.path).split("/")

        # Serve static files (css, js, images)
        if self.path.startswith('/static/'):
            self.serve_static_file()
            return
        
        # Serve the index.html file when the root is requested
        if self.path in ('/', '/index.html'):
            self.serve_file('templates/index.html', 'text/html')
            return

        if self.parsed_url[1] in httpGetHandler.GET_LIST:
            func_name = httpGetHandler.generateFuncName(self.parsed_url[1])
            func = getattr(httpGetHandler, func_name, lambda: "Invalid")
            func(self)
        
         # If no matching route or static file is found, return a 404
        self.send_error(HTTPStatus.NOT_FOUND, "File not found")
    
    def serve_static_file(self):
        # Remove the leading '/static/' from the path
        file_path = self.path[len('/static/'):]
        file_path = os.path.join('static', file_path)
        
        # Security check: do not serve hidden files or climb above the static directory
        if not os.path.normpath(file_path).startswith(os.path.join(os.getcwd(), 'static')) or file_path.startswith('.'):
            self.send_error(HTTPStatus.FORBIDDEN, "Access denied")
            return
        
        # Check if the file exists
        if not os.path.exists(file_path):
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        
        # Determine the content type
        content_type = 'text/plain' # default to text/plain
        if file_path.endswith('.css'):
            content_type = 'text/css'
        elif file_path.endswith('.js'):
            content_type = 'application/javascript'
        elif file_path.endswith('.html'):
            content_type = 'text/html'
        
        self.serve_file(file_path, content_type)

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as file:
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except OSError:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Failed to read file")

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
