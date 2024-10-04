import logging
import os
import logging
import cv2
import numpy as np
from flask import Flask, send_from_directory, Response
from flask_socketio import SocketIO

# ------------------------------------------------------------------------------------ #
from src import setup
from src import camera
from src.http_server import get_handler, post_handler, session_handler, get_handler_socket

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "FLASK"

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
# ------------------------------------------------------------------------------------ #

script_dir = os.path.dirname(os.path.realpath(__file__))
react_folder = f"{script_dir}/react_app"

app = Flask(__name__, static_folder=f"{react_folder}/build/static", template_folder=f"{react_folder}/build")
app.register_blueprint(get_handler.blueprint)
app.register_blueprint(post_handler.blueprint)

socketio = SocketIO(app)
session = session_handler.Session(socketio)
get_handler_socket.register_socket_events(socketio, session)


def gen_image():
    compression_params = [cv2.IMWRITE_WEBP_QUALITY, 20]
    resolution_scale = 0.8
    frame_width, frame_height = (
        int(camera.CAMERA.get_width() * resolution_scale),
        int(camera.CAMERA.get_height() * resolution_scale),
    )

    def _create_dummy_image():
        frame = np.zeros((frame_width, frame_height, 3), dtype=np.uint8)
        cv2.putText(frame, f"Camera offline", (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame

    while True:
        frame = camera.CAMERA.frame

        if frame is None:
            frame = _create_dummy_image()

        frame = cv2.resize(frame, (frame_width, frame_height))
        _, img = cv2.imencode(".webp", frame, compression_params)

        if img is not None:
            yield (b"--frame\r\n" b"Content-Type: image/webp\r\n\r\n" + img.tobytes() + b"\r\n")


@app.route("/cctv")
def img():
    return Response(gen_image(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/")
def serve():
    return send_from_directory(app.template_folder, "index.html")


# ------------------------------------------------------------------------------------ #
def start():
    host = "0.0.0.0"
    port = setup.MASTER_SERVER_PORT
    CLI.printline(Level.INFO, "({:^10}) Started Flask Server at port {:^4}".format(print_name, port))
    app.run(host=host, port=port)
