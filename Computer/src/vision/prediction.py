import os
import numpy as np
import cv2
import socket

# ------------------------------------------------------------------------------------------------ #
# from rknn.api import RKNN           #for tinker
# from rknnlite.api import RKNNLite     #for rock
from src import CLI
from src.CLI import Level

hostname = socket.gethostname()
use_rknnlite = "cage" in hostname and int(hostname.split("cage")[1].split("x")[0]) > 1

# Determine if we need to use RKNN or RKNNLite based on the hostname
if use_rknnlite:
    from rknnlite.api import RKNNLite  # Import RKNNLite
    RKNN_MODEL = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "yolov5_m1_rock_v2.rknn",
    )
else:
    from rknn.api import RKNN  # Import RKNN
    RKNN_MODEL = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "yolov5_m1_v2.rknn",
    )



BOX_THRESH = 0.5
NMS_THRESH = 0.6
IMG_SIZE = (640, 640)
CLASSES = "egg"


# ------------------------------------------------------------------------------------------------ #
class ComputerVision:
    def __init__(self):
        self.rknn_ready = False
        # self.rknn = RKNN() #for tinker
        # self.rknn = RKNNLite() #for rock
        if use_rknnlite:
            self.rknn = RKNNLite()  # Use RKNNLite if the condition is met
        else:
            self.rknn = RKNN()

    def load_rknn_model(self):
        if not os.path.exists(RKNN_MODEL):
            CLI.printline(Level.ERROR, "(RKNN) model does not exist")
            return
        CLI.printline(Level.INFO, "(RKNN) Loading model..........")
        ret = self.rknn.load_rknn(RKNN_MODEL)
        if ret != 0:
            CLI.printline(Level.ERROR, "(RKNN) Load yolo-V5 failed!")
            return
        CLI.printline(Level.INFO, "(RKNN) Init runtime environment........")
        ret = self.rknn.init_runtime()
        # ret = rknn.init_runtime('rk1808', device_id='1808')
        if ret != 0:
            CLI.printline(Level.ERROR, "(RKNN) Init runtime environment failed")
            return
        CLI.printline(Level.INFO, "(RKNN) Model Loaded")
        self.rknn_ready = True

    def is_rknn_ready(self):
        return self.rknn_ready

    def get_rknn(self):
        return self.rknn

    # ------------------------------------------------------------------------------------------------ #

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def xywh2xyxy(self, x):
        # Convert [x, y, w, h] to [x1, y1, x2, y2] in-place
        x[:, 0] -= x[:, 2] / 2  # top left x
        x[:, 1] -= x[:, 3] / 2  # top left y
        x[:, 2] += x[:, 0]  # bottom right x
        x[:, 3] += x[:, 1]  # bottom right y
        return x

    def process(self, input, mask, anchors):
        """
        Process the output of the neural network to convert it into a format that
        can be used to extract bounding box coordinates, object confidence, and class
        probabilities.

        # Arguments
            input: nd-array, raw output from the neural network.
            mask: list, mask indices to be applied to the anchors.
            anchors: nd-array, anchor boxes used to decode the predicted boxes.

        # Returns
            box: nd-array, transformed bounding box coordinates (x, y, width, height).
            box_confidence: nd-array, object confidence score.
            box_class_probs: nd-array, class probabilities.

        # Processing Steps
            - Anchors are filtered and reshaped based on the mask.
            - Box confidence and class probabilities are computed using the sigmoid function.
            - Box x and y coordinates are adjusted based on a grid and scaled relative to input size.
            - Box width and height are adjusted based on the anchors and scaled exponentially.
        """
        anchors = np.array([anchors[i] for i in mask])

        grid_h, grid_w = input.shape[:2]
        input_size = np.array([IMG_SIZE[1], IMG_SIZE[0]])

        # Compute box confidence and class probabilities
        box_confidence = self.sigmoid(input[..., 4:5])
        box_class_probs = self.sigmoid(input[..., 5:])

        # Compute box xy coordinates
        box_xy = self.sigmoid(input[..., :2]) * 2 - 0.5
        grid = np.meshgrid(np.arange(grid_w), np.arange(grid_h))
        grid = np.expand_dims(np.stack(grid, axis=-1), axis=2)
        box_xy += grid
        box_xy *= input_size / (grid_w, grid_h)

        # Compute box width and height
        box_wh = np.power(self.sigmoid(input[..., 2:4]) * 2, 2)
        box_wh *= anchors

        box = np.concatenate((box_xy, box_wh), axis=-1)

        return box, box_confidence, box_class_probs

    def filter_boxes(self, boxes, box_confidences, box_class_probs):
        """
        Filter boxes based on object confidence threshold and class score threshold.

        # Arguments
            boxes: nd-array, boxes of objects.
            box_confidences: nd-array, confidences of objects.
            box_class_probs: nd-array, class_probs of objects.

        # Returns
            boxes: nd-array, filtered boxes.
            classes: nd-array, classes for boxes.
            scores: nd-array, scores for boxes.
        """
        # Reshape the boxes, confidences and class_probs arrays for consistency
        boxes = boxes.reshape(-1, 4)
        box_confidences = box_confidences.reshape(-1)
        box_class_probs = box_class_probs.reshape(-1, box_class_probs.shape[-1])

        # Filter out boxes with object confidence below the threshold
        _box_pos = np.where(box_confidences >= BOX_THRESH)
        boxes = boxes[_box_pos]
        box_confidences = box_confidences[_box_pos]
        box_class_probs = box_class_probs[_box_pos]

        # Determine the class with the maximum score for each box
        class_max_score = np.max(box_class_probs, axis=-1)
        classes = np.argmax(box_class_probs, axis=-1)

        # Further filter boxes based on class score and object confidence
        _class_pos = np.where(class_max_score * box_confidences >= BOX_THRESH)

        # Apply the class-based filtering to boxes, classes, and scores
        boxes = boxes[_class_pos]
        classes = classes[_class_pos]
        scores = (class_max_score * box_confidences)[_class_pos]

        return boxes, classes, scores

    def nms_boxes(self, boxes, scores):
        """
        Perform Non-Maximum Suppression (NMS) to eliminate boxes with lower confidence scores.

        # Arguments
            boxes: nd-array, boxes of objects.
            scores: nd-array, scores of objects.

        # Returns
            keep: nd-array, indices of the boxes that have been kept after NMS.
        """

        # Extract coordinates for each box and calculate areas
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]
        areas = (x2 - x1) * (y2 - y1)

        # Sort scores in descending order and get the indices
        order = scores.argsort()[::-1]

        keep = []  # List to keep the indices of the selected boxes

        # Perform NMS by checking the overlap of each box with higher-score boxes
        while order.size > 0:
            i = order[0]  # Index of the current box with the highest score
            keep.append(i)

            # Calculate the intersection of the boxes
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            # Calculate the area of overlap
            w = np.maximum(0.0, xx2 - xx1 + 0.00001)
            h = np.maximum(0.0, yy2 - yy1 + 0.00001)
            intersection = w * h

            # Calculate the IoU (Intersection over Union)
            iou = intersection / (areas[i] + areas[order[1:]] - intersection)

            # Keep boxes where the IoU is below the threshold
            below_threshold_indices = np.where(iou <= NMS_THRESH)[0]
            order = order[below_threshold_indices + 1]

        return np.array(keep)

    def yolov5_post_process(self, input_data):
        """
        Post-processes the output of the YOLOv5 model, applying filtering and non-maximum suppression (NMS).
        Args:
        - input_data: The raw output from the YOLOv5 model.

        Returns:
        - boxes: The filtered bounding box coordinates.
        - classes: The class indices corresponding to the boxes.
        - scores: The confidence scores of the boxes.
        """

        # Define masks and anchors used in the process
        masks = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        anchors = [[10, 13], [16, 30], [33, 23], [30, 61], [62, 45], [59, 119], [116, 90], [156, 198], [373, 326]]

        # Lists to store all boxes, classes, and scores across different masks
        all_boxes, all_classes, all_scores = [], [], []

        # Iterate over each mask and apply processing and filtering
        for input, mask in zip(input_data, masks):
            b, c, s = self.process(input, mask, anchors)  # Process each mask
            b, c, s = self.filter_boxes(b, c, s)  # Filter boxes based on confidence scores

            # Extend the lists with the results
            all_boxes.extend(b)
            all_classes.extend(c)
            all_scores.extend(s)

        # If no boxes were detected, return None
        if not all_classes and not all_scores:
            return None, None, None

        # Convert box coordinates from xywh to xyxy format
        all_boxes = self.xywh2xyxy(np.array(all_boxes))
        all_classes = np.array(all_classes)
        all_scores = np.array(all_scores)

        # Identify unique classes detected
        unique_classes = set(all_classes)

        # Lists to store the final filtered boxes, classes, and scores
        final_boxes, final_classes, final_scores = [], [], []

        # Apply non-maximum suppression (NMS) separately for each detected class
        for c in unique_classes:
            indices = np.where(all_classes == c)

            class_boxes = all_boxes[indices]
            class_scores = all_scores[indices]

            keep = self.nms_boxes(class_boxes, class_scores)  # Apply NMS

            # Append the NMS-filtered boxes, class indices, and scores to the final lists
            final_boxes.append(class_boxes[keep])
            final_classes.append(np.full(len(keep), c))
            final_scores.append(class_scores[keep])

        # Concatenate results across all classes to get the final output
        return (np.concatenate(final_boxes), np.concatenate(final_classes), np.concatenate(final_scores))

    def draw(self, image, boxes, scores, classes):
        """Draw the boxes on the image.

        # Argument:
            image: original image.
            boxes: nd-array, boxes of objects.
            classes: nd-array, classes of objects.
            scores: nd-array, scores of objects.
            all_classes: all classes name.
        """
        for box, score, cl in zip(boxes, scores, classes):
            top, left, right, bottom = box
            ##        print('class: {}, score: {}'.format(CLASSES[cl], score))
            ##        print('box coordinate left,top,right,down: [{}, {}, {}, {}]'.format(top, left, right, bottom))
            top = int(top)
            left = int(left)
            right = int(right)
            bottom = int(bottom)

            cv2.rectangle(image, (top, left), (right, bottom), (255, 0, 0), 1)
            cv2.putText(
                image,
                "{0} {1:.2f}".format(CLASSES[cl], score),
                (top, left - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                1,
            )
        return image

    def letterbox(self, im, new_shape=(640, 640), color=(0, 0, 0)):
        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

        # Compute padding
        ##    ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return im

    def pre_process(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = self.letterbox(frame, new_shape=(IMG_SIZE[1], IMG_SIZE[0]))
        return img

    def prepare_inference_data(self, outputs):
        input_data = []
        for i in range(3):
            input_i_data = outputs[i]
            input_i_data = input_i_data.reshape([3, -1] + list(input_i_data.shape[-2:]))
            input_data.append(np.transpose(input_i_data, (2, 3, 0, 1)))

        # Process the input data using yolov5_post_process
        boxes, classes, scores = self.yolov5_post_process(input_data)
        return boxes, classes, scores
