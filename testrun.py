from imutils.video import VideoStream
from flask import Response, Flask
import threading
import time
import imutils
import cv2

# initialize the video stream and allow the camera sensor to warm up
# Change this for raspberryPiCam
# vs = VideoStream(usePiCamera=1).start()

outputFrame = None
lock = threading.Lock()


class Testrun:
    def __init__(self):
        self.vs = VideoStream(src=0).start()
        time.sleep(2.0)

    def generate(self):
        global lock, outputFrame
        # loop over frames from the output stream
        while True:
            # wait until the lock is acquired
            with lock:
                # check if the output frame is available, otherwise skip
                # the iteration of the loop
                if outputFrame is None:
                    continue

                # encode the frame in JPEG format
                (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

                # ensure the frame was successfully encoded
                if not flag:
                    continue

                # yield the output frame in the byte format
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

    def detect(self, speed):
        # grab global references to the video stream, output frame, and
        # lock variables
        global lock, outputFrame
        # loop over frames from the video stream
        while True:
            # read the next frame from the video stream, resize it,
            # convert the frame to grayscale, and blur it
            frame = self.vs.read()
            frame = imutils.resize(frame, width=650)

            # acquire the lock, set the output frame, and release the
            # lock
            with lock:
                outputFrame = frame.copy()
