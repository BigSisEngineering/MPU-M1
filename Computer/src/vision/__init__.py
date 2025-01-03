import threading
import os
import numpy as np
import socket

# ------------------------------------------------------------------------------------------------ #
from src import CLI, comm
from src.CLI import Level
from src import setup
from src import data
from src.vision.prediction import ComputerVision_y10, ComputerVision

hostname = socket.gethostname()
use_rknnlite = "cage" in hostname and int(hostname.split("cage")[1].split("x")[0]) > 1
model = data.model


# Determine if we need to use RKNN or RKNNLite based on the hostname
if use_rknnlite:
    from rknnlite.api import RKNNLite  # Import RKNNLite

    if model == "v10":
        RKNN_MODEL = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "yolov10s_rock_v2.rknn",
        )
    else:
        RKNN_MODEL = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "yolov5l_m1_rock_v2.rknn",
        )

else:
    from rknn.api import RKNN  # Import RKNN

    if model == "v5c3":
        RKNN_MODEL = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "yolov5_m1_3c.rknn",
        )
    else:
        RKNN_MODEL = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "yolov5_m1_v2.rknn",
        )


def get_misalignment(circle_center, radius, bbox):
    x_min, y_min, x_max, y_max = bbox
    top_circle = (circle_center[0], circle_center[1] - radius)
    bottom_circle = (circle_center[0], circle_center[1] + radius)
    top_edge_point = (top_circle[0], y_min)
    bottom_edge_point = (bottom_circle[0], y_max)
    top_line_length = np.linalg.norm(np.array(top_circle) - np.array(top_edge_point))
    bottom_line_length = np.linalg.norm(np.array(bottom_circle) - np.array(bottom_edge_point))
    if top_line_length > bottom_line_length:
        return top_line_length, "top"
    else:
        return bottom_line_length, "bottom"


class ProcessAndPrediction:
    def __init__(self):
        if model == "v10":
            self.computer_vision = ComputerVision_y10()
        else:
            self.computer_vision = ComputerVision()

        self.boxes = None
        self.classes = None
        self.scores = None
        threading.Thread(target=self.computer_vision.load_rknn_model).start()
        self.desired_width = 640
        self.desired_height = 480

    @comm.timer()
    def is_egg_detected(self, image, confident_level=0.80):
        if self.computer_vision.is_rknn_ready():
            # Calculate the top-left corner of the cropping rectangle
            x1 = max(setup.CENTER_X - self.desired_width // 2, 0)
            y1 = max(setup.CENTER_Y - self.desired_height // 2, 0)

            # Ensure the cropping rectangle does not exceed the image bounds
            x2 = min(x1 + self.desired_width, image.shape[1])
            y2 = min(y1 + self.desired_height, image.shape[0])

            # Adjust x1 and y1 in case x2 or y2 are out of bounds
            if x2 - x1 < self.desired_width:
                x1 = max(x2 - self.desired_width, 0)
            if y2 - y1 < self.desired_height:
                y1 = max(y2 - self.desired_height, 0)

            # Crop the image
            image = image[y1:y2, x1:x2]
            with data.pnp_vision_lock:
                if (use_rknnlite and model == "v10") or model == "v5c3":
                    # Get the detections (boxes, classes, scores)
                    self.boxes, self.classes, self.scores = self.computer_vision.prepare_inference_data(
                        self.computer_vision.get_rknn().inference(inputs=[self.computer_vision.pre_process(image)])
                    )

                    egg_count = 0
                    crack_detected = False

                    # Check for eggs (class 0) and cracks (class 2)
                    for i, class_id in enumerate(self.classes):
                        score = self.scores[i]
                        if class_id == 0 and score > confident_level:  # Class 0: Egg
                            egg_count += 1
                        elif class_id == 2:  # and score > 0.35:  # Class 2: Crack
                            crack_detected = True

                    # if self.boxes is not None:
                    #     adjusted_center_x = setup.CENTER_X - x1
                    #     adjusted_center_y = setup.CENTER_Y - y1
                    #     circle_center = (adjusted_center_x, adjusted_center_y)
                    #     for i,cls in enumerate(self.classes):
                    #         if cls == 1:  # Check if the class is 1
                    #             line_length, line_position = get_misalignment(circle_center, setup.RADIUS, self.boxes[i])
                    #             print(f'line length : {line_length}, line position : {line_position}')

                    # Logic for returning based on detection
                    if egg_count > 0:
                        print(f"egg detected {egg_count}")
                        return egg_count  # Return number of eggs detected
                    elif crack_detected:
                        print("crack detected")
                        return 99  # Crack detected but no eggs with high confidence
                    else:
                        return 0

                else:
                    image = self.computer_vision.letterbox(image)
                    self.boxes, self.classes, self.scores = self.computer_vision.prepare_inference_data(
                        self.computer_vision.get_rknn().inference(inputs=[self.computer_vision.pre_process(image)])
                    )
                    print(self.scores, self.boxes, self.classes)
                    if self.scores is not None:
                        egg_list = [score for score in self.scores if score > confident_level]
                        return len(egg_list)

        return 0  # No eggs or cracks detected with sufficient confidence


PNP = ProcessAndPrediction()


# [0.7108973] [[254.26714 339.85162 282.50098 371.06683]] [0]
