import cv2
import numpy as np

from src import data


def process_image(image, center_point, radius):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(img, data.white_shade, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        print(f"Area : {cv2.contourArea(largest_contour)}")
        is_inside = cv2.pointPolygonTest(largest_contour, center_point, False)
        contour_image_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(contour_image_bgr, [largest_contour], -1, (0, 255, 0), 2)
        if is_inside >= 0:
            print("center inside")
            line_length = process_center_inside(binary, center_point, contour_image_bgr)
        else:
            print("center outside")
            line_length = process_center_outside(binary, center_point, largest_contour, contour_image_bgr)

        print(f"Line Length: {line_length} pixels, Radius: {radius} pixels")

        # combined_image = np.concatenate((image, contour_image_bgr), axis=1)
        return contour_image_bgr
    return image


def process_center_inside(binary, center_point, contour_image_bgr):
    y_up = y_down = None
    for y in range(center_point[1], -1, -1):
        if binary[y, center_point[0]] == 0:
            y_up = y + 1
            break
    for y in range(center_point[1], binary.shape[0]):
        if binary[y, center_point[0]] == 0:
            y_down = y - 1
            break
    if y_up is not None and y_down is not None:
        cv2.line(contour_image_bgr, (center_point[0], y_up), (center_point[0], y_down), (255, 0, 0), 2)
        return y_down - y_up
    return 0


def process_center_outside(binary, center_point, largest_contour, contour_image_bgr):
    # Calculate moments of the largest contour to find the centroid
    M = cv2.moments(largest_contour)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else:
        cX, cY = 0, 0  # Default to (0,0) if contour is somehow degenerate

    # Determine if the centroid is above or below the center point
    if cY < center_point[1]:
        print("Centroid above center")
        direction = "above"
    else:
        print("Centroid below center")
        direction = "below"

    # Find intersection point by scanning in the appropriate direction
    intersection_point = None
    if direction == "above":
        for y in range(center_point[1], -1, -1):  # Scan upwards
            if cv2.pointPolygonTest(largest_contour, (center_point[0], y), False) >= 0:
                intersection_point = (center_point[0], y)
                break
    else:
        for y in range(center_point[1], binary.shape[0]):  # Scan downwards
            if cv2.pointPolygonTest(largest_contour, (center_point[0], y), False) >= 0:
                intersection_point = (center_point[0], y)
                break

    # Draw the line if an intersection point was found
    if intersection_point:
        cv2.line(contour_image_bgr, center_point, intersection_point, (255, 0, 0), 2)
        return abs(center_point[1] - intersection_point[1])
    return 0
