import cv2
import numpy as np
import threading
import subprocess
import time
import os
import math
from skimage.feature import canny
from skimage.transform import hough_circle, hough_circle_peaks

from datetime import datetime  # NOTE FOR TESTING ONLY

# ------------------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level
from src import setup


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



def find_circle(img, crop_factor=1, resize_factor=1):
    """
    mask out everything but the green pot
    `crop_factor` scales the mask by some amount
    `resize` resizes the image for computing the mask
    """
    if resize_factor != 1:
        img = cv2.resize(img, (0,0), fx=resize_factor, fy=resize_factor)

    # Resize the image to 960x720 first
    # img = cv2.resize(img, (960, 720))
    
    hough_radii = np.arange(int(0.21*img.shape[0]), int(0.31*img.shape[0]), math.ceil(0.01*img.shape[0]))
    canny_img = canny(img.mean(axis=-1), sigma=2, low_threshold=10, high_threshold=40)
    hough_res = hough_circle(canny_img, hough_radii)
    _, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii, total_num_peaks=5)
    argmin = np.argmin(radii)
    
    mask = np.zeros_like(img).sum(axis=-1).astype(np.uint8)
    cv2.circle(mask, (round(int(cx[argmin]/resize_factor)),
                      round(int(cy[argmin]/resize_factor))),
               round(int((radii[argmin]+1)*crop_factor/resize_factor)), 1, -1)
    
    mask_coordinates = (int(cx[argmin]/resize_factor), int(cy[argmin]/resize_factor), int((radii[argmin]+1)*crop_factor/resize_factor))
    
    setup.save_mask_coordinates(mask_coordinates)
    
    # img[~mask.astype(bool)] = 0
    return mask 

def CircularMask(image):
    mask = np.zeros_like(image)
    cv2.circle(mask, (setup.CENTER_X, setup.CENTER_Y), setup.RADIUS, (255, 255, 255), -1)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image
    
    

class CameraThreading:
    def __init__(self, camera_id: int):
        self.camera_id = camera_id
        self.frame_lock = threading.Lock()
        self.raw_frame = None  # NOTE FOR TESTING ONLY
        self.ctn = 0

    def start_frame_update(self, killer: threading.Event):
        if self.camera_id is None:
            CLI.printline(Level.ERROR, "(CameraThreading)-Camera ID error")
            # FIXME
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            CLI.printline(Level.ERROR, f"(CameraThreading)-Could not open video capture")
        else:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)  # FIXME -
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # FIXME
        
        i =0
        while not killer.is_set():
            try:
                ret, raw_frame = cap.read()
                i+=1
                if i ==1:
                    frame = find_circle(frame)
                if not ret:
                    try:
                        CLI.printline(Level.ERROR, f"(CameraThreading)-Could not read frame")
                        cap = cv2.VideoCapture(getUSBCameraID())
                        if not cap.isOpened():
                            CLI.printline(Level.ERROR, f"(CameraThreading)-Could not open video capture")
                        else:
                            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)  # FIXME -
                            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # FIXME
                        time.sleep(1)
                        continue  # non-return thread
                    except Exception as e:
                        CLI.printline(Level.ERROR, f"(CameraThreading)-{e}")
                # CLI.printline(Level.DEBUG, "(camera)-Frame Captured")
                # Update frame
                if self.frame_lock.acquire(timeout=1 / 24):
                    self.raw_frame = raw_frame
                    self.frame_lock.release()
                    # CLI.printline(Level.WARNING, "(camera)-Frames updated")

            except Exception as e:
                CLI.printline(Level.ERROR, f"(CameraThreading)-{e}")
            else:
                pass

        cap.release()
        CLI.printline(Level.ERROR, f"(CameraThreading)-Frame Update thread terminated.")

    def get_frame(self):
        with self.frame_lock:
            frame = self.raw_frame
        if frame is not None:
            # Crop and rotate
            height, width, _ = frame.shape
            # Calculate the coordinates for cropping#
            size = 640
            top = (height - size) // 2
            bottom = top + size
            left = (width - size) // 2
            right = left + size
            frame = frame[top:bottom, left:right]  # Expected the size
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        return frame

    def get_raw_frame(self):
        with self.frame_lock:
            frame = self.raw_frame
        return frame

    def save_frame(self):
        with self.frame_lock:
            file_name = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                f"{self.ctn}.jpg",
            )
            cv2.imwrite(f"{file_name}", self.shared_frame)
            self.ctn += 1
            # print(f"Image saved: {file_name} ")

    def save_raw_frame(
        self, frame, confident: float = 0.0, prediction: int = 0, arg_timestamp_now: datetime = None
    ):  # NOTE FOR TESTING ONLY
        def take_a_shot(frame):
            if arg_timestamp_now is None:
                timestamp_now = datetime.now()
            else:
                timestamp_now = arg_timestamp_now

            timestamp = timestamp_now.strftime("%Y%m%d%H%M%S")
            timestamp_ms = timestamp_now.strftime("%f")[:2]
            # [CAGE_ID]_[DATE][TIME]_[CONFIDENCE]_[RESULT].jpg
            file_name = os.path.join(
                # os.path.dirname(os.path.realpath(__file__)),
                "/dev/shm",
                f"{setup.CAGE_ID}_{timestamp}{timestamp_ms}_{int(confident*100)}_{prediction}.jpg",
            )
            cv2.imwrite(f"{file_name}", frame)
            print(f"Image saved: {file_name} ")

        threading.Thread(target=take_a_shot, args=(frame,)).start()


# ------------------------------------------------------------------------------------------------ #
KILLER = threading.Event()
CAMERA = CameraThreading(getUSBCameraID())


def create_thread():
    global KILLER
    return threading.Thread(target=CAMERA.start_frame_update, args=(KILLER,))