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

bbox = ComputerVision()
def gen():
    original_width, original_height = 640, 480
    new_shape = (640, 640)
    # original_center_x = setup.CENTER_X
    # original_center_y = setup.CENTER_Y
    # original_radius = setup.RADIUS
    # # Calculate the scale ratio and padding used by letterbox
    # scale = min(new_shape[0] / original_height, new_shape[1] / original_width)
    # new_unpad = (int(round(original_width * scale)), int(round(original_height * scale)))
    # dw = (new_shape[1] - new_unpad[0]) // 2
    # dh = (new_shape[0] - new_unpad[1]) // 2

    # # Adjust the center and radius based on the letterbox transformation
    # center_x = int(original_center_x * scale) + dw
    # center_y = int(original_center_y * scale) + dh
    # radius = int(original_radius * scale)

    def _create_dummy_image():
        frame = np.zeros((new_shape[1], new_shape[0], 3), dtype=np.uint8)
        cv2.putText(
            frame,
            "Camera Offline",
            (50, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        return frame

    while True:
        frame = camera.CAMERA.get_frame()
        if frame is None:
            print("Frame is None, creating dummy image")
            frame = _create_dummy_image()
        else:
            frame = bbox.letterbox(frame)
            if vision.PNP.boxes is not None:
                # print("Drawing bounding boxes")
                frame = bbox.draw(
                    frame,
                    vision.PNP.boxes,
                    vision.PNP.scores,
                    vision.PNP.classes
                )

        #     # Ensure the values are within bounds
        #     y1 = max(center_y - radius, 0)
        #     y2 = min(center_y + radius, frame.shape[0])
        #     x1 = max(center_x - radius, 0)
        #     x2 = min(center_x + radius, frame.shape[1])

            # try:
            #     # Crop the frame
            #     frame = frame[y1:y2, x1:x2]
            #     # Debugging prints
            #     # print(f"Frame shape after cropping: {frame.shape}")
            # except Exception as e:
            #     print(f"Error during cropping: {e}")

        try:
            img = cv2.imencode(".jpg", frame)[1].tobytes()
            if img is not None:
                yield (b"--frame\r\n" b"Content-Type: image/jpg\r\n\r\n" + img + b"\r\n")
            else:
                print("Image encoding failed")
        except Exception as e:
            print(f"Error during image encoding: {e}")


@app.route("/video_feed")
def video_feed():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")


# ============================================== #
def start_server(host="0.0.0.0", port=8080):
    CLI.printline(Level.INFO, "({:^10}) Started Server.".format(print_name))
    app.run(host=host, port=port)
