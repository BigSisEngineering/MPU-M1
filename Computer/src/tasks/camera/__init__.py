import cv2
import numpy as np
import threading
import subprocess
import os
import socket
import logging
from datetime import datetime, timedelta  # NOTE FOR TESTING ONLY

# ------------------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level
from src import setup
from src.tasks import find_circle
from src import data

def getUSBCameraID():
    try:
        #   ┌─────────────────────────────────────────────────────────────────────────────┐
        #   │         # Looking for the info like:                                        │
        #   │         # rkisp1_mainpath (platform:ff920000.rkisp1):                       │
        #   │         #         /dev/video5                                               │
        #   │         #         /dev/video6                                               │
        #   │         #         /dev/video7                                               │
        #   │                                                                             │
        #   │         # HD USB Camera (usb-xhci-hcd.11.auto-1.3):                         │
        #   │         #         /dev/video10                                              │
        #   │         #         /dev/video11                                              │
        #   │         # where we can do the cv2.VideoCapture(ID)                          │
        #   └─────────────────────────────────────────────────────────────────────────────┘

        cmd = "v4l2-ctl --list-devices"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            lines = result.stdout.split("\n")
            ctn = 0
            for line in lines:
                ctn += 1
                if "USB" in line:  # Expect "HD USB Camera"
                    infos = lines[ctn].strip().split("/")  # Expect "/dev/video*"
                    for info in infos:
                        if "video" in info:
                            CLI.printline(Level.INFO, f"(getUSBCameraID)-Camera ID detected: {info}")
                            return (int)(info.replace("video", ""))
        else:
            CLI.printline(Level.ERROR, f"(getUSBCameraID) - {result.stderr}")
    except Exception as e:
        CLI.printline(Level.ERROR, f"(getUSBCameraID) - {e}")
    return None


class CameraThreading:
    def __init__(self, camera_id: int):
        self.camera_id = camera_id
        self.frame_lock = threading.Lock()
        self.shared_frame_lock = threading.Lock()
        self.raw_frame = None  # NOTE FOR TESTING ONLY
        self.ctn = 0
        self.w = 1080
        self.h = 960

        # ------------------------------------------------------------------------------------ #
        self._device_ready: bool = False
        self._lock_device_ready = threading.Lock()

    @property
    def device_ready(self):
        with self._lock_device_ready:
            r = self._device_ready
        return r

    def start_frame_update(self, killer: threading.Event):
        if self.camera_id is None:
            CLI.printline(Level.ERROR, "(CameraThreading)-Camera ID error")
            # FIXME
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            CLI.printline(Level.ERROR, f"(CameraThreading)-Could not open video capture")
        # else:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)  # FIXME -
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)  # FIXME
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # Disable auto-exposure
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        while not killer.is_set():
            try:
                ret, raw_frame = cap.read()
                if not ret:
                    try:
                        CLI.printline(Level.ERROR, f"(CameraThreading)-Could not read frame")
                        cap = cv2.VideoCapture(getUSBCameraID())
                        if not cap.isOpened():
                            CLI.printline(Level.ERROR, f"(CameraThreading)-Could not open video capture")
                        # else:
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)  # FIXME -
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)  # FIXME
                        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # Disable auto-exposure
                        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
                        # time.sleep(0.1)
                        continue  # non-return thread
                    except Exception as e:
                        CLI.printline(Level.ERROR, f"(CameraThreading)-{e}")
                # CLI.printline(Level.DEBUG, "(camera)-Frame Captured")
                # Update frame
                with self.frame_lock:
                    self.raw_frame = raw_frame
                    # CLI.printline(Level.WARNING, "(camera)-Frames updated")

            except Exception as e:
                CLI.printline(Level.ERROR, f"(CameraThreading)-{e}")
            else:
                pass

        cap.release()
        CLI.printline(Level.ERROR, f"(CameraThreading)-Frame Update thread terminated.")

    def get_frame(self):
        with self.frame_lock:
            try:
                frame = self.raw_frame
                if frame is not None:
                    with self._lock_device_ready:
                        self._device_ready = True
                    frame = find_circle.circular_mask(frame)
                else:
                    with self._lock_device_ready:
                        self._device_ready = False
                return frame

            except Exception as e:
                with self._lock_device_ready:
                    self._device_ready = False
                CLI.printline(Level.ERROR, f"(CameraThreading - get_frame)-{e}")

    def get_raw_frame(self):
        with self.frame_lock:
            frame = self.raw_frame
        return frame
    
    
    # def is_blurry(self):
    #     gray = cv2.cvtColor(self.get_frame(), cv2.COLOR_BGR2GRAY)
    #     # laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    #     # is_blurry = laplacian_var < threshold
    #     # print(f"Blurry: {'Yes' if is_blurry else 'No'} | Score: {laplacian_var:.2f}")
    #     # return is_blurry
    #     sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    #     sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    #     gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    #     blurriness = np.mean(gradient_magnitude)
    #     is_blurry = blurriness < data.blur_threshold
    #     print(f"Blurry: {'Yes' if is_blurry else 'No'} | Score: {blurriness:.2f}")
    #     return is_blurry

    def save_raw_frame(
        self, frame, confident: float = 0.0, prediction: int = 0, arg_timestamp_now: datetime = None):  # NOTE FOR TESTING ONLY
        def take_a_shot(frame):
            if arg_timestamp_now is None:
                timestamp_now = datetime.now()
            else:
                timestamp_now = arg_timestamp_now

            timestamp = timestamp_now.strftime("%Y_%m_%d_%H_%M_%S_")
            timestamp_ms = timestamp_now.strftime("%f")[:2]
            # [CAGE_ID]_[DATE][TIME]_[CONFIDENCE]_[RESULT].jpg
            file_name = os.path.join(
                # os.path.dirname(os.path.realpath(__file__)),
                "/dev/shm",
                f"{setup.CAGE_ID}_{timestamp}{timestamp_ms}_{int(confident*100)}_{prediction}.jpg",
            )
            cv2.imwrite(f"{file_name}", frame)
            print(f"Image saved: {file_name} ")
            logging.info(file_name)

        threading.Thread(target=take_a_shot, args=(frame,)).start()


# ------------------------------------------------------------------------------------------------ #
KILLER = threading.Event()
CAMERA = CameraThreading(getUSBCameraID())


def create_thread():
    global KILLER
    return threading.Thread(target=CAMERA.start_frame_update, args=(KILLER,))
