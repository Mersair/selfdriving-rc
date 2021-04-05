import argparse
from imutils.video import VideoStream
import time
import socketio
import base64
import cv2
import numpy as np
from datetime import datetime
import json

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
        self.drive = False
        self.exit = False
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


# streamer = CVClient('ai-car.herokuapp.com', [255, 255, 255], [0, 0, 0])
streamer = CVClient('127.0.0.1:5000', [255, 255, 255], [0, 0, 0])
@sio.on('carid2cv', namespace='/cv')
def set_car_id(carid):
    # make sure the car does not already have an id

    if streamer.car_id == 'none':
        # set the car id to the streamer
        print('setting car id to', carid)
        streamer.car_id = carid

        # write it to a file on the car
        f = open("/etc/selfdriving-rc/car_id.txt", "w")
        f.write(carid)
        f.close()

        # socket connection for coordinates to be sent to the car
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

        # socket connection to reset the colors on the car
        resetcolors2cv_string = 'resetcolors2cv/' + streamer.car_id
        @sio.on(resetcolors2cv_string, namespace='/cv')
        def reset_color_channels():
            streamer.higher_channels = [0, 0, 0]
            streamer.lower_channels = [255, 255, 255]

        # socket on terminate driving
        terminate2cv_string = 'terminate2cv/' + streamer.car_id
        @sio.on(terminate2cv_string, namespace='/cv')
        def terminate():
            streamer.exit = True

        # socket to reset drive trigger
        stop2cv_string = 'stop2cv/' + streamer.car_id
        @sio.on(stop2cv_string, namespace='/cv')
        def stop_driving():
            streamer.drive = False

        # socket on start driving
        drive2cv_string = 'drive2cv/' + streamer.car_id
        @sio.on(drive2cv_string, namespace='/cv')
        def drive():
            streamer.drive = True

    else:
        print('car\'s id is already', streamer.car_id)


def main(server_addr, speed, steering, lower_channels, higher_channels):
    global streamer, output_frame, filtered_frame
    vs = VideoStream(src=0).start()
    last_time = datetime.now()
    time.sleep(2.0)

    streamer = CVClient(server_addr, lower_channels, higher_channels)
    streamer.setup()
    sio.sleep(2.0)

    while True:
        if streamer.exit:
            break

        if streamer.drive:
            print("driving")

        frame = vs.read()
        # frame = imutils.resize(frame, width=650)

        scale = 45
        width = int(frame.shape[1] * scale / 100)
        height = int(frame.shape[0] * scale / 100)
        dim = (width, height)
        frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

        output_frame = frame.copy()
        filtered_frame = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2HSV)
        masked = cv2.inRange(filtered_frame, np.array(streamer.lower_channels), np.array(streamer.higher_channels))

        this_time = datetime.now()
        time_difference = this_time - last_time
        if time_difference.total_seconds() >= 0.2:
            #streamer.send_video_feed(output_frame, 'cvimage2server')
            #streamer.send_video_feed(masked, 'cvfiltered2server')
            last_time = this_time

    print("terminating driving code")
    sio.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MQP Dashboard Video Streamer')
    # parser.add_argument(
    #         '--server-addr',  type=str, default='ai-car.herokuapp.com',
    #         help='The IP address or hostname of the SocketIO server.')
    parser.add_argument(
            '--server-addr',  type=str, default='127.0.0.1:5000',
            help='The IP address or hostname of the SocketIO server.')
    parser.add_argument("--speed", help="Car Speed", default=0)
    parser.add_argument("--steering", help="Car Steering", default=100)
    parser.add_argument("--lowerArr", help="Lower Color Channel", default=[255, 255, 255])
    parser.add_argument("--higherArr", help="Higher Color Channel", default=[0, 0, 0])
    args = parser.parse_args()
    main(args.server_addr, args.speed, args.steering, args.lowerArr, args.higherArr)
