import cv2
import threading
import time
import numpy as np
import subprocess

# ============================================== #
from src._shared_variables import SV

# ============================================== #
from src import CLI
from src.CLI import Level

print_name = "CAMERA"


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
                if "USB" in line or "Webcam" in line:  # Expect "HD USB Camera"
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


class CameraStream:
    def __init__(self, width=1280, height=720, fps=30) -> None:
        self.src = None
        self.stream = None

        self._lock_frame = threading.Lock()
        self._frame = None

        self.width = width
        self.height = height
        self.fps = fps

        self._init_camera()

        self._device_ready = False

        # update frame
        # threading.Thread(target=self._update).start()

    # -------------------------------------------------------- #
    def _init_camera(self) -> None:
        self.src = getUSBCameraID()
        self.stream = cv2.VideoCapture(self.src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.stream.set(cv2.CAP_PROP_FPS, self.fps)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    def _refresh(self):
        self._init_camera()
        time.sleep(0.5)

    def _update(self) -> None:
        CLI.printline(Level.INFO, "({:^10}) Start Stream -> {}".format(print_name, self.src))
        while not SV.KILLER_EVENT.is_set():
            try:
                (_, _frame) = self.stream.read()
                if _frame is None:
                    self._refresh()
                    self._device_ready = False
                else:
                    with self._lock_frame:
                        self._frame = _frame
                    self._device_ready = True

            except Exception as e:
                CLI.printline(
                    Level.ERROR,
                    "({:^10})-({:^8}) Exception -> {}".format(print_name, "UPDATE", e),
                )
                self._device_ready = False
                self._refresh()

        CLI.printline(Level.INFO, "({:^10}) Stop Stream -> {}".format(print_name, self.src))

    # -------------------------------------------------------- #
    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    @property
    def frame(self):
        with self._lock_frame:
            _frame = self._frame
        return _frame

    @property
    def device_ready(self) -> bool:
        return self._device_ready


CAMERA = CameraStream()
