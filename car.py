from datetime import datetime
import cv2
import imutils
import time
import json
from imutils.video import VideoStream
import threading
import numpy as np
from redisConn import RedisConn

outputFrame = None
filteredFrame = None
lock = threading.Lock()

class Car:
    def __init__(self):
        # initialize the video stream and allow the camera sensor to warm up
        # Change this for raspberryPiCam
        # vs = VideoStream(usePiCamera=1).start()
        # self.vs = VideoStream(src=0).start()
        time.sleep(2.0)
        self.timestamp = []
        self.hall_effect_data = []
        self.battery_data = []
        self.temperature_data = []
        self.humidity_data = []
        self.imu_data = []
        self.speed = 50
        self.lower_channels = [255, 255, 255]
        self.higher_channels = [0, 0, 0]
        self.isDriving = False
        self.speed = 0.2
        self.speedRange = (0.0, 0.25) #Highest and lowest throttle speed

    # Return the last N entries or as many entries we have, whichever is lower
    def lastNEntries(self, arr, entries):
        if (len(arr) < entries):
            entries = len(arr)
        return arr[-entries:]

    def storeSensorReadings(self, sensor_readings):
        # Append the new readings to the historic data
        self.timestamp.append(datetime.now().strftime('%H:%M:%S'))
        self.hall_effect_data.append(sensor_readings['hall_effect'])
        self.battery_data.append(sensor_readings['battery'])
        self.temperature_data.append(sensor_readings['temperature'])
        self.humidity_data.append(sensor_readings['humidity'])
        self.imu_data.append(sensor_readings['imu'])

    # Get the last stores entries as a dictionary
    def readData(self):
        return {
            "timestamp": self.lastNEntries(self.timestamp, 30),
            "hall_effect": self.lastNEntries(self.hall_effect_data, 30),
            "battery": self.lastNEntries(self.battery_data, 30),
            "temperature": self.lastNEntries(self.temperature_data, 30),
            "humidity": self.lastNEntries(self.humidity_data, 30),
            "imu": self.lastNEntries(self.imu_data, 30)
    }

    # Return data to front end for export
    def export_sensor_data(self):
        return {
            "timestamp": self.timestamp,
            "hall_effect": self.hall_effect_data,
            "battery": self.battery_data,
            "temperature": self.temperature_data,
            "humidity": self.humidity_data,
            "imu": self.imu_data
        }

    # Get the speed of the car
    def getSpeed(self):
        return {
            "speed": self.speed
        }

    # Set the speed of the car
    def setSpeed(self, speed):
        self.speed = speed

    # Reset the car's color channels
    def resetColorChannels(self):
        self.lower_channels = [255, 255, 255]
        self.higher_channels = [0, 0, 0]
        return {
            "lower_channels": self.lower_channels,
            "higher_channels": self.higher_channels
        }

    # Get the car's color channels
    def getColorChannels(self):
        return {
            "lower_channels": self.lower_channels,
            "higher_channels": self.higher_channels
        }

    # Set the car's color channels
    def setColorChannels(self, x, y):
        global filteredFrame

        if filteredFrame is None:
            return "no output frame found"
        # x = 650 - x

        colorsH = int(filteredFrame[y, x, 0])
        colorsS = int(filteredFrame[y, x, 1])
        colorsV = int(filteredFrame[y, x, 2])
        self.checkNewHSVMinMax(colorsH, colorsS, colorsV)

        return {
            "lower_channels": self.lower_channels,
            "higher_channels": self.higher_channels
        }

    def checkNewHSVMinMax(self, h, s, v):
        if h < self.lower_channels[0]:
            self.lower_channels[0] = h
        if s < self.lower_channels[1]:
            self.lower_channels[1] = s
        if v < self.lower_channels[2]:
            self.lower_channels[2] = v
        if h > self.higher_channels[0]:
            self.higher_channels[0] = h
        if s > self.higher_channels[1]:
            self.higher_channels[1] = s
        if v > self.higher_channels[2]:
            self.higher_channels[2] = v

    # Prints to dashboard
    def print_data(self):
        last_length = 0
        while True:
            if len(self.temperature_data) > last_length:
                last_length = len(self.temperature_data)
                json_data = json.dumps(
                    {
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'values': {
                            'imu': {
                                'x': self.imu_data[-1][0],
                                'y': self.imu_data[-1][1],
                                'z': self.imu_data[-1][2],
                            },
                            'hef': self.hall_effect_data[-1],
                            'bat': self.battery_data[-1],
                            'tmp': self.temperature_data[-1],
                            'hmd': self.humidity_data[-1],
                        }
                    }
                )
                yield f"data:{json_data}\n\n"
            time.sleep(1.5)

    def getStartupControls(self):
        return {
            "speed": self.speed,
            "lower_channels": self.lower_channels,
            "higher_channels": self.higher_channels
        }

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
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

    def generate_filtered(self):
        global lock, filteredFrame
        # loop over frames from the output stream
        while True:
            # wait until the lock is acquired
            with lock:
                # check if the output frame is available, otherwise skip
                # the iteration of the loop
                if filteredFrame is None:
                    continue

                masked = cv2.inRange(filteredFrame, np.array(self.lower_channels), np.array(self.higher_channels))
                # encode the frame in JPEG format
                (flag, encodedImage) = cv2.imencode(".jpg", masked)

                # ensure the frame was successfully encoded
                if not flag:
                    continue

                # yield the output frame in the byte format
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

    def detect(self):
        # grab global references to the video stream, output frame, and
        # lock variables
        global lock, outputFrame, filteredFrame
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
                filteredFrame = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2HSV)

    def startDriving(self, inputSpeed, lowerArr, higherArr):
        print(inputSpeed)
        print(lowerArr)
        print(higherArr)
