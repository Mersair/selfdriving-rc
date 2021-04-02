import numpy as np
import cv2


class ColorThreshholdFilter:
    isInit = None

    def __init__(self):
        self.isInit = False

    def apply(self, frame, rgb_min, rgb_max):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array(rgb_min), np.array(rgb_max))
        return mask
