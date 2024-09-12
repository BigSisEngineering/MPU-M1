import threading
import os
import numpy as np
import time
import cv2
import socket
import multiprocessing


# from rknn.api import RKNN           #for tinker
# from rknnlite.api import RKNNLite    #for rock

# ------------------------------------------------------------------------------------------------ #
from src import CLI, comm
from src.CLI import Level
from src import setup
from src import data
from src.vision.prediction import ComputerVision_y10, ComputerVision
from src.tasks import camera

hostname = socket.gethostname()
use_rknnlite = "cage" in hostname and int(hostname.split("cage")[1].split("x")[0]) > 1
model = data.model



# Determine if we need to use RKNN or RKNNLite based on the hostname
if use_rknnlite:
    from rknnlite.api import RKNNLite  # Import RKNNLite
    if model == 'v10':
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
    RKNN_MODEL = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "yolov5_m1_v2.rknn",
    )


queue_size = 1

frame_queue = multiprocessing.Queue(maxsize=queue_size)
detection_queue = multiprocessing.Queue(maxsize=queue_size)
results_queue = multiprocessing.Queue(maxsize=queue_size)
PROCESS_KILLER_EVENT = multiprocessing.Event()
WATCHDOG = 0.01
KILLER_EVENT = threading.Event()


class ProcessAndPrediction:
    
    def __init__(self):
        # if model == 'v10':
        #     self.computer_vision = ComputerVision_y10()
        # else:
        #     self.computer_vision = ComputerVision()

        self.boxes = None
        self.classes = None
        self.scores = None
        # threading.Thread(target=self.computer_vision.load_rknn_model).start()
        self.desired_width = 640
        self.desired_height = 480
    
    # ======================================================== #
    #                        SUBPROCESS                        #
    # ======================================================== #
    @staticmethod
    def _detection_subprocess():
        print('Start detection subprocess ...')
        time_stamp = time.time()
        if model == 'v10':
            computer_vision = ComputerVision_y10()
        else:
            computer_vision = ComputerVision()

        computer_vision.load_rknn_model()
        
        while not PROCESS_KILLER_EVENT.is_set():
            if (
                time.time() - time_stamp > WATCHDOG
                and frame_queue.full()
                and not detection_queue.full()
            ):
                frame = frame_queue.get()
                frame = computer_vision.letterbox(frame)
                outputs = computer_vision.get_rknn().inference(inputs=[computer_vision.pre_process(frame)])
                detection_queue.put(outputs)


    @staticmethod
    def _results_subprocess():
        print('Start results subprocess ...')
        time_stamp = time.time()
        if model == 'v10':
            computer_vision = ComputerVision_y10()
        else:
            computer_vision = ComputerVision()

        while not PROCESS_KILLER_EVENT.is_set():
            if (
                time.time() - time_stamp > WATCHDOG
                and detection_queue.full()
                and not results_queue.full()
            ):
                outputs = detection_queue.get()
                inference_data = computer_vision.prepare_inference_data(outputs)
                results_queue.put(inference_data)

    @comm.timer()
    def is_egg_detected(self,  confident_level=0.80):
        # if ComputerVision().is_rknn_ready():
        try:
            image = camera.CAMERA.get_frame()
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
            # image = camera.CAMERA.get_frame()
            print('after get frame')
            # Crop the image
            image = image[y1:y2, x1:x2]
            frame_queue.put(image)
            print('frame put into queueu')
            # while not KILLER_EVENT.is_set():
            if results_queue.full():
                # print('check resuelts queueu')
                inference_data = results_queue.get()  # get results
                self.boxes, self.classes, self.scores = inference_data
                # print(f'inference_data : {inference_data}')
                # break



            if use_rknnlite and model == 'v10':
                egg_count = 0
                crack_detected = False

                # Check for eggs (class 0) and cracks (class 2)
                for i, class_id in enumerate(self.classes):
                    score = self.scores[i]
                    if class_id == 0 and score > confident_level:  # Class 0: Egg
                        egg_count += 1
                    elif class_id == 2: #and score > 0.35:  # Class 2: Crack
                        crack_detected = True

                # Logic for returning based on detection
                if egg_count > 0:
                    print(f'egg detected {egg_count}')
                    return egg_count  # Return number of eggs detected
                elif crack_detected:
                    print('crack detected')
                    return 99  # Crack detected but no eggs with high confidence
                
            else:
                print(self.scores, self.boxes, self.classes)
                if self.scores is not None:
                    egg_list = [score for score in self.scores if score > confident_level]
                    return len(egg_list)
            
        except Exception as e:
            CLI.printline(Level.ERROR, f"(Vision - ProcessAndPrediction)-{e}")

            
        return 0  # No eggs or cracks detected with sufficient confidence



p1 = multiprocessing.Process(target=ProcessAndPrediction._detection_subprocess)
p2 = multiprocessing.Process(target=ProcessAndPrediction._results_subprocess)
p1.start()
p2.start()

PNP = ProcessAndPrediction()


#[0.7108973] [[254.26714 339.85162 282.50098 371.06683]] [0]