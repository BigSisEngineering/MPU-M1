import threading
import os
import numpy as np
import cv2
import socket

# from rknn.api import RKNN           #for tinker
# from rknnlite.api import RKNNLite    #for rock

# ------------------------------------------------------------------------------------------------ #
from src import CLI, comm
from src.CLI import Level
from src import setup
from src.vision.prediction import ComputerVision

hostname = socket.gethostname()
use_rknnlite = "cage" in hostname and int(hostname.split("cage")[1].split("x")[0]) > 1

# Determine if we need to use RKNN or RKNNLite based on the hostname
if use_rknnlite:
    from rknnlite.api import RKNNLite  # Import RKNNLite
    RKNN_MODEL = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "yolov5_m1_rock_v2.rknn",
    )
else:
    from rknn.api import RKNN  # Import RKNN
    RKNN_MODEL = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "yolov5_m1_v2.rknn",
    )

class ProcessAndPrediction:
    def __init__(self):
        self.computer_vision = ComputerVision()
        self.boxes= None
        self.classes= None
        self.scores= None
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

            image = image[y1:y2, x1:x2]

            image = self.computer_vision.letterbox(image)
            self.boxes, self.classes, self.scores = self.computer_vision.prepare_inference_data(
                self.computer_vision.get_rknn().inference(inputs=[self.computer_vision.pre_process(image)])
            )
            print(self.scores, self.boxes, self.classes)
            if self.scores is not None:
                egg_list = [score for score in self.scores if score > confident_level]
                return len(egg_list)
        return 0
        # Boxes can be ignore, the position of the egg
        # if classes is None == no egg
        # classes will be a list of zero, each zero will be an egg
        # scores is a list to each one


PNP = ProcessAndPrediction()