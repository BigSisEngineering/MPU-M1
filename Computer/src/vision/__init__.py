import threading
import os
import numpy as np
import cv2

from rknn.api import RKNN

# ------------------------------------------------------------------------------------------------ #
from src import CLI, comm
from src.CLI import Level

from src.vision.prediction import ComputerVision

RKNN_MODEL = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "yolov5_m1.rknn",
)


class ProcessAndPrediction:
    def __init__(self):
        self.computer_vision = ComputerVision()
        threading.Thread(target=self.computer_vision.load_rknn_model).start()

    @comm.timer()
    def is_egg_detected(self, image, confident_level=0.85):
        if self.computer_vision.is_rknn_ready():
            _, _, scores = self.computer_vision.prepare_inference_data(
                self.computer_vision.get_rknn().inference(inputs=[self.computer_vision.pre_process(image)])
            )
            print(scores)
            if scores is not None:
                egg_list = [score for score in scores if score > confident_level]
                return len(egg_list)
        return 0
        # Boxes can be ignore, the position of the egg
        # if classes is None == no egg
        # classes will be a list of zero, each zero will be an egg
        # scores is a list to each one


PNP = ProcessAndPrediction()