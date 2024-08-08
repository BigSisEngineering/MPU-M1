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


# def CircularMask(image):
#     # global CENTER_X, CENTER_Y, RADIUS
#     mask = np.zeros_like(image)
#     # CENTER_X, CENTER_Y, RADIUS = setup.read_mask_coordinates()
#     cv2.circle(mask, (setup.CENTER_X, setup.CENTER_Y), setup.RADIUS, (255, 255, 255), -1)
#     masked_image = cv2.bitwise_and(image, mask)
#     y1 = max(setup.CENTER_Y - setup.RADIUS, 0)
#     y2 = min(setup.CENTER_Y + setup.RADIUS, masked_image.shape[0])
#     x1 = max(setup.CENTER_X - setup.RADIUS, 0)
#     x2 = min(setup.CENTER_X + setup.RADIUS, masked_image.shape[1])
#     # print(f'y1 : {y1} - y2 : {y2} - x1 : {x1} - x2 - {x2}')
#     cropped_image = masked_image[y1:y2, x1:x2]
#     # print(f"cropped image size: {cropped_image.shape[1]}x{cropped_image.shape[0]}")
#     return cropped_image



def CircularMask(image):
    mask = np.zeros_like(image)
    cv2.circle(mask, (setup.CENTER_X, setup.CENTER_Y), setup.RADIUS, (255, 255, 255), -1)
    masked_image = cv2.bitwise_and(image, mask)

    # Desired dimensions for the cropped image
    desired_width = 640
    desired_height = 480

    # Calculate the top-left corner of the cropping rectangle
    x1 = max(setup.CENTER_X - desired_width // 2, 0)
    y1 = max(setup.CENTER_Y - desired_height // 2, 0)

    # Ensure the cropping rectangle does not exceed the image bounds
    x2 = min(x1 + desired_width, masked_image.shape[1])
    y2 = min(y1 + desired_height, masked_image.shape[0])

    # Adjust x1 and y1 in case x2 or y2 are out of bounds
    if x2 - x1 < desired_width:
        x1 = max(x2 - desired_width, 0)
    if y2 - y1 < desired_height:
        y1 = max(y2 - desired_height, 0)

    cropped_image = masked_image[y1:y2, x1:x2]

    return cropped_image

def FindCircleThread(stop_event: threading.Event):
    # global CIRCLE_FLAG, CENTER_X, CENTER_Y, RADIUS
    global CIRCLE_FLAG
    time_stamp = time.time()
    watchdog = 60  # seconds
    while not stop_event.is_set():
        try:
            if (time.time() - time_stamp) > watchdog:
                time_stamp = time.time()
                # with self.frame_lock:
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
