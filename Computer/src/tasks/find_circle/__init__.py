import cv2
import numpy as np
import threading
import math
from skimage.feature import canny
from skimage.transform import hough_circle, hough_circle_peaks

# ------------------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level
from src import setup
from src.tasks import camera
import time

KILLER = threading.Event()
CIRCLE_FLAG = False


def find_circle(img, crop_factor=1, resize_factor=1):
    """
    mask out everything but the green pot
    `crop_factor` scales the mask by some amount
    `resize` resizes the image for computing the mask
    """
    try:
        CLI.printline(Level.INFO, f"(findCircle)-start")
        if resize_factor != 1:
            img = cv2.resize(img, (0, 0), fx=resize_factor, fy=resize_factor)

        hough_radii = np.arange(int(0.21 * img.shape[0]), int(0.31 * img.shape[0]), math.ceil(0.01 * img.shape[0]))
        canny_img = canny(img.mean(axis=-1), sigma=2, low_threshold=10, high_threshold=40)
        hough_res = hough_circle(canny_img, hough_radii)

        if hough_res.size != 0 and hough_radii.size != 0:
            # FIXME -> extremely slow
            _, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii, total_num_peaks=5)
            argmin = np.argmin(radii)
            mask = np.zeros_like(img).sum(axis=-1).astype(np.uint8)
            cv2.circle(
                mask,
                (round(int(cx[argmin] / resize_factor)), round(int(cy[argmin] / resize_factor))),
                round(int((radii[argmin] + 1) * crop_factor / resize_factor)),
                1,
                -1,
            )

            setup.CENTER_X = int(cx[argmin] / resize_factor)
            setup.CENTER_Y = int(cy[argmin] / resize_factor)
            setup.RADIUS = int((radii[argmin] + 1) * crop_factor / resize_factor)

            # save values
            setup.save_mask_coordinates()

        CLI.printline(Level.INFO, f"(findCircle)-end")

    except Exception as e:
        CLI.printline(Level.ERROR, f"(findCircle)-{e}")


def circular_mask(image):
    mask = np.zeros_like(image)
    cv2.circle(mask, (setup.CENTER_X, setup.CENTER_Y), setup.RADIUS, (255, 255, 255), -1)
    masked_image = cv2.bitwise_and(image, mask)

    return masked_image

def find_circle_thread(stop_event: threading.Event):
    watchdog = 60  # seconds
    time_stamp = time.time() - watchdog  # instant first find

    while not stop_event.is_set():
        try:
            if (time.time() - time_stamp) > watchdog:
                if camera.CAMERA.device_ready:
                    # read raw frame
                    raw_frame = camera.CAMERA.get_raw_frame()

                    # update circle
                    find_circle(raw_frame)

                    # update time stamp at the end (60 seconds b/w each attempt)
                    time_stamp = time.time()

        except Exception as e:
            CLI.printline(Level.ERROR, f"(finding Circle)-{e}")
            continue


def create_thread():
    global KILLER
    return threading.Thread(target=find_circle_thread, args=(KILLER,))
