import numpy as np
import cv2

class ColorThreshholdFilter:
    isInit = None
    lower_red = None
    upper_red = None

    def __init__(self):
        self.isInit = False

    def apply(self, frame, rgb_min, rgb_max):

        if ((rgb_min[0] + rgb_min[1] + rgb_min[2]) == 0):
            rgb_min[0] = 1

        if (self.isInit == False):
            lower = np.array(rgb_min)
            upper = np.array(rgb_max)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)

        return mask