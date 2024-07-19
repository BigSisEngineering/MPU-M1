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
# CENTER_X = setup.CENTER_X
# CENTER_Y = setup.CENTER_Y
# RADIUS = setup.RADIUS
# CENTER_X, CENTER_Y, RADIUS = setup.read_mask_coordinates()

def FindCircle(img, crop_factor=1, resize_factor=1):
    """
    mask out everything but the green pot
    `crop_factor` scales the mask by some amount
    `resize` resizes the image for computing the mask
    """
    if resize_factor != 1:
        img = cv2.resize(img, (0, 0), fx=resize_factor, fy=resize_factor)

    # Resize the image to 960x720 first
    # img = cv2.resize(img, (960, 720))

    hough_radii = np.arange(int(0.21 * img.shape[0]), int(0.31 * img.shape[0]), math.ceil(0.01 * img.shape[0]))
    canny_img = canny(img.mean(axis=-1), sigma=2, low_threshold=10, high_threshold=40)
    hough_res = hough_circle(canny_img, hough_radii)
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
    # mask_coordinates = (
    #     int(cx[argmin] / resize_factor),
    #     int(cy[argmin] / resize_factor),
    #     int((radii[argmin] + 1) * crop_factor / resize_factor),
    # )

    # setup.save_mask_coordinates(mask_coordinates)
    setup.CENTER_X = int(cx[argmin] / resize_factor)
    setup.CENTER_Y = int(cy[argmin] / resize_factor)
    setup.RADIUS = int((radii[argmin] + 1) * crop_factor / resize_factor)
    
    # img[~mask.astype(bool)] = 0
    return mask


def CircularMask(image):
    # global CENTER_X, CENTER_Y, RADIUS
    mask = np.zeros_like(image)
    # CENTER_X, CENTER_Y, RADIUS = setup.read_mask_coordinates()
    cv2.circle(mask, (setup.CENTER_X, setup.CENTER_Y), setup.RADIUS, (255, 255, 255), -1)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image


def FindCircleThread(stop_event: threading.Event):
    # global CIRCLE_FLAG, CENTER_X, CENTER_Y, RADIUS
    global CIRCLE_FLAG
    time_stamp = time.time()
    watchdog = 5  # seconds
    while not stop_event.is_set():
        try:
            if (time.time() - time_stamp) > watchdog:
                time_stamp = time.time()
                if camera.CAMERA.get_frame() is not None:
                    print("finding circle ...")
                    FindCircle(camera.CAMERA.get_raw_frame())
                    CIRCLE_FLAG = True
                    # print(f"Circle found with coordinates {setup.CENTER_X}, {setup.CENTER_Y}, {setup.RADIUS}")
        except Exception as e:
            CLI.printline(Level.ERROR, f"(finding Circle)-{e}")
            continue


def create_thread():
    global KILLER
    return threading.Thread(target=FindCircleThread, args=(KILLER,))
