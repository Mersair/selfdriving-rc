# imports for driving
import cv2
import numpy as np
import time
from adafruit_servokit import ServoKit
from colorThreshholdFilter import ColorThreshholdFilter
import RPi.GPIO as GPIO

# imports for server
import argparse
from imutils.video import VideoStream
import socketio
import base64
from datetime import datetime
import json

# server event code
# for debugging on, use
# sio = socketio.Client(logger=True, engineio_logger=True)
sio = socketio.Client()
output_frame = None
filtered_frame = None

@sio.event(namespace='/cv')
def connect():
    print('[INFO] Connected to server.')

@sio.event(namespace='/cv')
def connect_error():
    print('[INFO] Failed to connect to server.')

@sio.event(namespace='/cv')
def disconnect():
    print('[INFO] Disconnected from server.')


class CVClient(object):
    def __init__(self, server_addr, lower_channels, higher_channels):
        self.car_id = 'none'
        self.server_addr = server_addr
        self.lower_channels = lower_channels
        self.higher_channels = higher_channels

    def setup(self):
        print('[INFO] Connecting to server http://{}...'.format(
            self.server_addr))
        sio.connect(
            'http://{}'.format(self.server_addr),
            transports=['websocket'],
            namespaces=['/cv'])
        time.sleep(2.0)
        return self

    def check_exit(self):
        pass

    def close(self):
        sio.disconnect()

    def _convert_image_to_jpeg(self, image):
        # masked = cv2.inRange(image, np.array(lower_channels), np.array(higher_channels))
        # encode the frame in JPEG format
        (flag, encodedImage) = cv2.imencode(".jpg", image)
        frame = encodedImage.tobytes()
        # Encode frame in base64 representation and remove
        # utf-8 encoding
        frame = base64.b64encode(frame).decode('utf-8')
        return "data:image/jpeg;base64,{}".format(frame)
        # yield the output frame in the byte format
        # return (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

    def send_video_feed(self, frame, route):
        sio.emit(
            route,
            {
                'carid': self.car_id,
                'image': self._convert_image_to_jpeg(frame)
            },
            namespace='/cv'
        )

    # Set the car's color channels
    def set_color_channels(self, x, y):
        global filtered_frame

        if filtered_frame is None:
            return "no output frame found"
        # x = 650 - x

        h = int(filtered_frame[y, x, 0])
        s = int(filtered_frame[y, x, 1])
        v = int(filtered_frame[y, x, 2])
        self.check_new_hsv(h, s, v)

    def check_new_hsv(self, h, s, v):
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


streamer = CVClient('ai-car.herokuapp.com', [255, 255, 255], [0, 0, 0])
@sio.on('carid2cv', namespace='/cv')
def set_car_id(carid):
    if streamer.car_id == 'none':
        print('setting car id to', carid)
        streamer.car_id = carid

        coordinates2cv_string = 'coordinates2cv/' + streamer.car_id
        @sio.on(coordinates2cv_string, namespace='/cv')
        def coordinates_to_hsv(message):
            json_data = json.loads(message)
            streamer.set_color_channels(json_data['x'], json_data['y'])
            color_channels = json.dumps({
                "carid": carid,
                "lower_channels": streamer.lower_channels,
                "higher_channels": streamer.higher_channels
            })
            sio.emit('channels2server', color_channels, namespace='/cv')

        resetcolors2cv_string = 'resetcolors2cv/' + streamer.car_id
        @sio.on(resetcolors2cv_string, namespace='/cv')
        def reset_color_channels():
            streamer.higher_channels = [0, 0, 0]
            streamer.lower_channels = [255, 255, 255]

    else:
        print('car\'s id is already', streamer.car_id)


def main(server_addr, speed, steering, lower_channels, higher_channels):
    global streamer, output_frame, filtered_frame
    # vs = VideoStream(src=0).start()
    cap = cv2.VideoCapture(0)
    last_time = datetime.now()
    time.sleep(2.0)

    streamer = CVClient(server_addr, lower_channels, higher_channels)
    streamer.setup()
    sio.sleep(2.0)

    # ser=serial.Serial("/dev/ttyACM0",9600)  #change ACM number as found from ls /dev/tty/ACM*
    # ser.baudrate=960

    colorThreshholdFilter = ColorThreshholdFilter()
    kit = ServoKit(channels=16)  # Initializes the servo shield
    kit.servo[0].angle = 90  # Sets wheels forward
    kit.continuous_servo[1].throttle = 0  # Sets speed to zero

    kit.servo[0].angle = 90

    while True:
        # frame = vs.read()
        # frame = imutils.resize(frame, width=650)

        # Take each frame
        _, frame = cap.read()
        height, width, channels = frame.shape
        middle = width / 2

        # The following code segments the camera input to do different calculations
        frame1init = frame[150:300, 0:int(int(width) / 3)]
        frame3 = frame[(height - 60):(height - 20),
                 int(int(width) / 3):int(2 * int(width) / 3)]  # Frame 3 gets the bottom of the screen
        frame2init = frame[150:300, int(2 * int(width) / 3):int(width)]

        # these are the color filters. The values are the RGB min and max values. the color filter makes every pixel in that range white and everything else black
        # CHANGE THESE VALUES FOR THE LANES
        frame1 = colorThreshholdFilter.apply(frame1init, [92, 115, 149], [100, 247, 199])
        frame2 = colorThreshholdFilter.apply(frame2init, [92, 115, 149], [100, 247, 199])

        scale = 75
        web_width = int(frame.shape[1] * scale / 100)
        web_height = int(frame.shape[0] * scale / 100)
        dim = (web_width, web_height)
        output_frame = cv2.resize(frame.copy(), dim, interpolation=cv2.INTER_AREA)

        filtered_frame = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2HSV)
        masked = colorThreshholdFilter.apply(filtered_frame, streamer.lower_channels, streamer.higher_channels)

        this_time = datetime.now()
        time_difference = this_time - last_time
        if time_difference.total_seconds() >= 0.2:
            streamer.send_video_feed(output_frame, 'cvimage2server')
            streamer.send_video_feed(masked, 'cvfiltered2server')
            last_time = this_time

        if streamer.check_exit():
            streamer.close()
            break

        # These two look at the color filtered images and gets the median of the lanes.
        leftlane = np.median([coordinate[1] for coordinate in np.argwhere(frame1 == 255)])
        rightlane = (2 * int(width) / 3) + np.median([coordinate[1] for coordinate in np.argwhere(frame2 == 255)])

        # This code just sees the difference from the middle
        offsetl = (middle - leftlane)
        offsetr = (rightlane - middle)

        # If no pixels are detected it means that the lane is far away (out of camera FOV). This code just sets the lane as far away.
        if np.isnan(offsetr):
            offsetr = 300
        if np.isnan(offsetl):
            offsetl = 300

        # This code just turns the offsets into a percentage value
        offset = offsetr - offsetl
        peroffset = offset / (width)

        # This code sets a hard limit for the turn angle. This is to reduce the stress on the wheel joints
        if peroffset > 0.33:
            peroffset = 0.33
        if peroffset < -0.33:
            peroffset = -0.33

        # This transforms the percentage into proper angle format
        angleset = 90 + (180 * peroffset)

        # Sets the angle
        kit.servo[0].angle = angleset

        # kit.continuous_servo[1].throttle = (0.3*(1-(2*abs(peroffset)))) #This is an option equation for slowing down in turns. We have to play around with the numbers.
        kit.continuous_servo[1].throttle = speed  # This sets the speed for the car. the range is 0 to 1. 0.15 is the slowest it can go in our tests.

    kit.continuous_servo[1].throttle = 0
    kit.servo[0].angle = 90
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MQP Dashboard Video Streamer')
    parser.add_argument(
            '--server-addr',  type=str, default='ai-car.herokuapp.com',
            help='The IP address or hostname of the SocketIO server.')
    parser.add_argument("--speed", help="Car Speed", default=0)
    parser.add_argument("--steering", help="Car Steering", default=100)
    parser.add_argument("--lowerArr", help="Lower Color Channel", default=[255, 255, 255])
    parser.add_argument("--higherArr", help="Higher Color Channel", default=[0, 0, 0])
    args = parser.parse_args()
    main(args.server_addr, args.speed, args.steering, args.lowerArr, args.higherArr)


