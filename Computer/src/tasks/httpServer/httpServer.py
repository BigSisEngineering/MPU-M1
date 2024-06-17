import http.server
import time
import threading
import os
from urllib.parse import unquote
from http import HTTPStatus
import cv2
import numpy as np

# ------------------------------------------------------------------------------------------------ #
from src.tasks.httpServer import httpGetHandler, httpPostHandler
from src import CLI
from src.CLI import Level
from src.tasks import camera

KILLER = threading.Event()


def generate_error_frame(message="Camera Error"):
    # Create a black image
    error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Define font, size, and color
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (0, 0, 255)  # Red color
    thickness = 2
    # Get the text size
    text_size = cv2.getTextSize(message, font, font_scale, thickness)[0]
    # Calculate the center position
    text_x = (error_frame.shape[1] - text_size[0]) // 2
    text_y = (error_frame.shape[0] + text_size[1]) // 2
    # Put the text on the image
    cv2.putText(error_frame, message, (text_x, text_y), font, font_scale, color, thickness)
    return error_frame


class httpHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # print(f"Current Working Directory: {os.getcwd()}")
            self.parsed_url = (self.path).split("/")

            # Serve static files (css, js, images)
            if self.path.startswith("/static/"):
                self.serve_static_file()
                return

            # Serve the index.html file when the root is requested
            if self.path in ("/", "/index.html"):
                self.serve_file(
                    "index.html", "text/html"
                )  # Corrected to serve index.html with the correct content type
                return

            # self.do_camera_stream()
            if self.path.startswith("/video10") or self.path.startswith("/video11"):
                self.do_camera_stream()
                return

            if self.parsed_url[1] in httpGetHandler.GET_LIST:
                func_name = httpGetHandler.generateFuncName(self.parsed_url[1])
                func = getattr(httpGetHandler, func_name, lambda: "Invalid")
                func(self)
            else:
                # If no matching route or static file is found, return a 404
                self.send_error(HTTPStatus.NOT_FOUND, "File not found")
        except Exception as e:
            # Handle other kinds of exceptions which might be critical
            CLI.printline(Level.ERROR, f"An unexpected error occurred: {e}")

    def do_camera_stream(self):
        self.send_response(200)
        self.send_header("Content-type", "multipart/x-mixed-replace; boundary=frame")
        self.end_headers()

        frame = camera.CAMERA.get_frame()
        if frame is None:
            CLI.printline(Level.ERROR, "Failed to encode frame.")
            frame = generate_error_frame("Camera Error")
        else:
            ret, jpeg = cv2.imencode(".jpg", frame)
            if ret:
                try:
                    self.wfile.write(b"--frame\r\n")
                    self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                    self.wfile.write(jpeg.tobytes())
                    self.wfile.write(b"\r\n")
                    time.sleep(0.1)
                except Exception as e:
                    CLI.printline(Level.ERROR, f"(do_camera_stream)-{e}")

    def serve_static_file(self):
        file_path = self.path[len("/static/") :]  # Correctly removes '/static/' from the path
        file_path = os.path.join("src", "tasks", "httpServer", "static", file_path)  # Adjusted path
        content_type = "text/plain"  # Default to text/plain
        if file_path.endswith(".css"):
            content_type = "text/css"
        elif file_path.endswith(".js"):
            content_type = "application/javascript"
        elif file_path.endswith(".html"):
            content_type = "text/html"
        self.serve_file(file_path, content_type)

    def serve_file(self, file_path, content_type):
        # For templates directory
        if "index.html" in file_path:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_dir, "templates", file_path)
        else:  # For static files
            base_dir = os.getcwd()
            full_path = os.path.join(base_dir, file_path)
        try:
            with open(full_path, "rb") as file:
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except OSError as e:
            print(f"Failed to read file {full_path}: {e}")
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Failed to read file")

    def do_POST(self):
        self.parsed_url = (self.path).split("/")
        if self.parsed_url[1] in httpPostHandler.POST_LIST:
            func_name = httpPostHandler.generateFuncName(self.parsed_url[1])
            func = getattr(httpPostHandler, func_name, lambda: "Invalid")
            func(self)

    def log_message(self, format, *args):
        return


def start_server(stop_event: threading.Event = KILLER, PORT=8080):
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
