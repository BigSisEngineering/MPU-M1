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
import os

# ============================================== #
from src import CLI
from src.CLI import Level
from src import data

print_name = "FLASK"

# ============================================== #
from src.tasks.httpServer import httpGetHandler, httpPostHandler
from src.tasks import camera
# from src.tasks import checkAlignment
from src import setup
from src import vision
from src.vision.prediction import ComputerVision, ComputerVision_y10


log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

#
# app = Flask(__name__, static_url_path="/static")  # flask app

script_dir = os.path.dirname(os.path.realpath(__file__))
react_folder = f"{script_dir}/react_app"

#
app = Flask(
    __name__,
    static_folder=f"{react_folder}/build/static",
    template_folder=f"{react_folder}/build",
)

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


bbox = ComputerVision_y10() if data.model == 'v10' else ComputerVision()


def gen():
    new_shape = (480, 320)
    # Desired dimensions for the cropped image
    desired_width = 640
    desired_height = 480

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

    def _add_top_right_text(frame, text, line_offset=0, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, color=(0, 255, 0), thickness=2):
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = frame.shape[1] - text_size[0] - 10
        text_y = text_size[1] + 10 + line_offset
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness)
    
    def _draw_lines_to_bbox(frame, circle_center, radius, bbox):
        """
        Draws perpendicular lines from the top and bottom points of the circle to the bounding box edges.

        Args:
        - frame: The frame (image) on which to draw.
        - circle_center: A tuple representing the (x, y) coordinates of the circle center.
        - radius: The radius of the circle.
        - bbox: A tuple representing the bounding box in (x_min, y_min, x_max, y_max) format.

        Returns:
        - frame: The frame with the lines drawn.
        """
        x_min, y_min, x_max, y_max = bbox
        
        # # Debugging info
        # print(f'Circle center: {circle_center}, radius: {radius}', flush=True)
        # print(f'Bounding box: {bbox}', flush=True)
        
        # Top and bottom points of the circle
        top_circle = (circle_center[0], circle_center[1] - radius)
        bottom_circle = (circle_center[0], circle_center[1] + radius)
        
        # Ensure coordinates are within the frame size to avoid out-of-bound errors
        if top_circle[1] < 0 or bottom_circle[1] >= frame.shape[0] or x_min < 0 or x_max >= frame.shape[1]:
            print("Invalid coordinates for drawing.", flush=True)
            return frame
        
        # Perpendicular lines from the top and bottom of the circle to the top and bottom edges of the bounding box
        top_edge_point = (top_circle[0], y_min)  # Same x as top_circle, y is the top edge of the box (y_min)
        bottom_edge_point = (bottom_circle[0], y_max)  # Same x as bottom_circle, y is the bottom edge of the box (y_max)
        
        # Draw lines from the top and bottom points of the circle to the bounding box
        cv2.line(frame, top_circle, top_edge_point, (255, 0, 0), 2)  # Blue line from top of circle to top edge of bbox
        cv2.line(frame, bottom_circle, bottom_edge_point, (255, 0, 0), 2)  # Blue line from bottom of circle to bottom edge of bbox

        return frame



        
    while True:
        frame = camera.CAMERA.get_frame()
        if frame is None:
            print("Frame is None, creating dummy image")
            frame = _create_dummy_image()
        else:
            # Calculate the top-left corner of the cropping rectangle
            x1 = max(setup.CENTER_X - desired_width // 2, 0)
            y1 = max(setup.CENTER_Y - desired_height // 2, 0)

            # Ensure the cropping rectangle does not exceed the image bounds
            x2 = min(x1 + desired_width, frame.shape[1])
            y2 = min(y1 + desired_height, frame.shape[0])

            # Adjust x1 and y1 in case x2 or y2 are out of bounds
            if x2 - x1 < desired_width:
                x1 = max(x2 - desired_width, 0)
            if y2 - y1 < desired_height:
                y1 = max(y2 - desired_height, 0)


            # Adjust the circle's center coordinates relative to the cropped frame
            adjusted_center_x = setup.CENTER_X - x1
            adjusted_center_y = setup.CENTER_Y - y1
            circle_center = (adjusted_center_x, adjusted_center_y)

            frame = frame[y1:y2, x1:x2]
            if data.model != 'v10':
                frame = bbox.letterbox(frame)
            if vision.PNP.boxes is not None:
                frame = bbox.draw(
                    frame,
                    vision.PNP.boxes,
                    vision.PNP.scores,
                    vision.PNP.classes
                )

            # if data.model == 'v10' and vision.PNP.classes is not None:
            #     # try:
            #     # print('inside the looppp....')
            #     for i,cls in enumerate(vision.PNP.classes):
            #         if cls == 1:  # Check if the class is 1
            #             print('found class 1 ...')
            #             frame = _draw_lines_to_bbox(frame, circle_center, setup.RADIUS, vision.PNP.boxes[i])
            #             break
        with data.lock:
            _add_top_right_text(frame, f"pots last hour : {data.eggs_last_hour}")
            _add_top_right_text(frame, f"steps last hour : {data.steps_last_hour}", line_offset=40)

        try:
            img = cv2.imencode(".jpg", frame)[1].tobytes()
            if img is not None:
                yield (b"--frame\r\n" b"Content-Type: image/jpg\r\n\r\n" + img + b"\r\n")
            else:
                print("Image encoding failed")
        except Exception as e:
            print(f"Error during image encoding: {e}")


# def gen_alignment():
#     new_shape = (480, 320)
#     def _create_dummy_image():
#         frame = np.zeros((new_shape[1], new_shape[0], 3), dtype=np.uint8)
#         cv2.putText(
#             frame,
#             "Camera Offline",
#             (50, 240),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             1,
#             (0, 255, 0),
#             2,
#         )
#         return frame
    
#     while True:
#         frame = camera.CAMERA.get_frame()
#         if frame is None:
#             # print("Frame is None, creating dummy image")
#             frame = _create_dummy_image()
#         else:
#             # Calculate the top-left corner of the cropping rectangle
#             frame = checkAlignment.process_image(frame, (setup.CENTER_X, setup.CENTER_Y), setup.RADIUS)

#         try:
#             img = cv2.imencode(".jpg", frame)[1].tobytes()
#             if img is not None:
#                 yield (b"--frame\r\n" b"Content-Type: image/jpg\r\n\r\n" + img + b"\r\n")
#             else:
#                 print("Image encoding failed")
#         except Exception as e:
#             print(f"Error during image encoding: {e}")


@app.route("/video_feed")
def video_feed():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")

# @app.route("/video_feed_alignment")
# def video_feed_alignment():
#     return Response(gen_alignment(), mimetype="multipart/x-mixed-replace; boundary=frame")


# ============================================== #
def start_server(host="0.0.0.0", port=8080):
    CLI.printline(Level.INFO, "({:^10}) Started Server.".format(print_name))
    app.run(host=host, port=port)
