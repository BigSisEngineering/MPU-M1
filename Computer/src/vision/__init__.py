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

from src.vision.prediction import ComputerVision

hostname = socket.gethostname()
use_rknnlite = "cage" in hostname and int(hostname.split("cage")[1].split("x")[0]) > 1

# Determine if we need to use RKNN or RKNNLite based on the hostname
if use_rknnlite:
    from rknnlite.api import RKNNLite  # Import RKNNLite
    RKNN_MODEL = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "yolov5_m1_rock.rknn",
    )
else:
    from rknn.api import RKNN  # Import RKNN
    RKNN_MODEL = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "yolov5_m1.rknn",
    )

class ProcessAndPrediction:
    def __init__(self):
        self.computer_vision = ComputerVision()
        self.boxes= None
        self.classes= None
        self.scores= None
        threading.Thread(target=self.computer_vision.load_rknn_model).start()

    @comm.timer()
    def is_egg_detected(self, image, confident_level=0.80):
        if self.computer_vision.is_rknn_ready():
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