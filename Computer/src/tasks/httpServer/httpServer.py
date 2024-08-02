from flask import (
    Flask,
    render_template,
    Response,
    redirect,
    url_for,
    make_response,
)
from flask_cors import CORS
import cv2
import numpy as np
import logging

# ============================================== #
from src import CLI
from src.CLI import Level

print_name = "FLASK"

# ============================================== #
from src.tasks.httpServer import httpGetHandler, httpPostHandler
from src.tasks import camera
from src import setup
from src import vision
from src.vision.prediction import ComputerVision


log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

#
app = Flask(__name__, static_url_path="/static")  # flask app
CORS(app)

app.register_blueprint(httpGetHandler.get_api)
app.register_blueprint(httpPostHandler.post_api)

@app.route("/")
def index():
    title = f"{setup.CAGE_ID}"

    return render_template(
        "index.html",
        title=title,
    )

def gen(gate: int):
    frame_width, frame_height = 640, 480
    center_x = setup.CENTER_X
    center_y = setup.CENTER_Y
    radius = setup.RADIUS

    def _create_dummy_image(camera: int):
        frame = np.zeros((frame_width, frame_height, 3), dtype=np.uint8)
        cv2.putText(
            frame,
            f"Camera {camera} Offline",
            (50, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        return frame

    while True:
        # frame = ComputerVision().letterbox()
        frame = camera.CAMERA.get_frame()
        if frame is None:
            frame = _create_dummy_image(gate)

        else:
            if vision.PNP.boxes is not None:
                frame = ComputerVision().draw(
                    frame,
                    vision.PNP.boxes,
                    vision.PNP.scores,
                    vision.PNP.classes,
                )
            # frame = cv2.resize(frame, (frame_width, frame_height))
            frame = frame[max(center_y - radius, 0):min(center_y + radius, frame.shape[0]), max(center_x - radius, 0):min(center_x + radius, frame.shape[1])]


        img = cv2.imencode(".jpg", frame)[1].tobytes()

        if img is not None:
            yield (b"--frame\r\n" b"Content-Type: image/jpg\r\n\r\n" + img + b"\r\n")


@app.route("/video_feed")
def video_feed():
    return Response(gen(1), mimetype="multipart/x-mixed-replace; boundary=frame")


# ============================================== #
def start_server(host="0.0.0.0", port=8080):
    CLI.printline(Level.INFO, "({:^10}) Started Server.".format(print_name))