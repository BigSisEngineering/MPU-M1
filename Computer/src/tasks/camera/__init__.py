import cv2
import numpy as np
import threading
import subprocess
import time
import os
import math
from skimage.feature import canny
from skimage.transform import hough_circle, hough_circle_peaks
import socket
import logging
from datetime import datetime, timedelta  # NOTE FOR TESTING ONLY

# ------------------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level
from src import setup
from src.tasks import findCircle
from src import vision
from src.vision.prediction import ComputerVision

# Ensure the log file is created if it doesn't exist
log_file = f'{socket.gethostname()}.log'
if not os.path.exists(log_file):
    open(log_file, 'a').close()

# Set up the logger
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(message)s'
)

def delete_old_files_from_log(log_file, days_old=4):
    # Read the log file
    def read_log_file(file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
                return [line.strip() for line in lines]
        else:
            logging.error(f"Log file {file_path} does not exist.")
            return []

    # Parse the timestamp from the filename
    def parse_timestamp_from_filename(filename):
        parts = filename.split('_')
        if len(parts) == 10:
            timestamp_str = f"{parts[1]}-{parts[2]}-{parts[3]} {parts[4]}:{parts[5]}:{parts[6]}"
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        return None

    # Calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=days_old)
    remaining_files = []

    # Process the log file
    file_paths = read_log_file(log_file)
    for path in file_paths:
        filename = os.path.basename(path)
        timestamp = parse_timestamp_from_filename(filename)

        if timestamp and timestamp < cutoff_date:
            try:
                os.remove(path)
                logging.info(f"Deleted file: {path}")
            except Exception as e:
                logging.error(f"Error deleting file {path}: {e}")
        else:
            remaining_files.append(path)

    # Update the log file
    with open(log_file, 'w') as file:
        for line in remaining_files:
            file.write(f"{line}\n")

    print("Old files deleted and log file updated.")

# Call the function to delete old files and update the log file
delete_old_files_from_log(log_file, days_old=4)


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
        self.bbox_lock = threading.Lock()
        self.raw_frame = None  # NOTE FOR TESTING ONLY
        self.ctn = 0

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
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1440)  # FIXME -
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # FIXME
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # Disable auto-exposure
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
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1440)  # FIXME -
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # FIXME
                        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # Disable auto-exposure
                        # time.sleep(0.1)
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

    # def start_frame_update(self, killer: threading.Event):
    #     if self.camera_id is None:
    #         CLI.printline(Level.ERROR, "(CameraThreading)-Camera ID error")
    #     cap = cv2.VideoCapture(self.camera_id)
    #     if not cap.isOpened():
    #         CLI.printline(Level.ERROR, f"(CameraThreading)-Could not open video capture")

    #     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1440)
    #     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    #     # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # Disable auto-exposure

    #     while not killer.is_set():
    #         try:
    #             ret, raw_frame = cap.read()
    #             if not ret:
    #                 CLI.printline(Level.ERROR, f"(CameraThreading)-Could not read frame, attempting to reconnect...")
    #                 cap.release()  # Ensure to release the previous capture object
    #                 # time.sleep(0.5)  # Optional: Sleep for a short duration before retrying
    #                 self.camera_id = getUSBCameraID()  # Re-fetch the camera ID
    #                 if self.camera_id is not None:
    #                     cap = cv2.VideoCapture(self.camera_id)
    #                     cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1440)
    #                     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    #                     # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
    #                     if cap.isOpened():
    #                         CLI.printline(Level.INFO, f"(CameraThreading)-Camera reconnected successfully.")
    #                     else:
    #                         CLI.printline(Level.ERROR, f"(CameraThreading)-Failed to reconnect.")
    #                         continue
    #                 else:
    #                     CLI.printline(Level.ERROR, f"(CameraThreading)-Failed to get a valid camera ID.")
    #                     continue
    #             # Update frame
    #             if self.frame_lock.acquire(timeout=1 / 24):
    #                 self.raw_frame = raw_frame
    #                 self.frame_lock.release()
    #         except Exception as e:
    #             CLI.printline(Level.ERROR, f"(CameraThreading)-{e}")

    #     cap.release()
    #     CLI.printline(Level.INFO, f"(CameraThreading)-Frame Update thread terminated.")


    def get_frame(self):
        with self.frame_lock:
            try:
                frame = self.raw_frame
                if frame is not None:
                    with self._lock_device_ready:
                        self._device_ready = True
                    # print(f'circle coordinates {findCircle.CENTER_X}, {findCircle.CENTER_Y}, {findCircle.RADIUS}')
                    frame = findCircle.CircularMask(frame)
                    # with self.bbox_lock:
                    #     frame = ComputerVision().letterbox(frame)
                    #     if vision.PNP.boxes is not None:
                    #         ComputerVision().draw(frame,vision.PNP.boxes,vision.PNP.scores, vision.PNP.classes)
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
