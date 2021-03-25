import argparse
from imutils.video import VideoStream
import time
import socketio
import base64
import cv2
import imutils
import numpy as np
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

    def _convert_image_to_jpeg(self, image, lower_channels, higher_channels):
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
                'image': self._convert_image_to_jpeg(frame, self.lower_channels, self.higher_channels)
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


def main(server_addr, lower_channels, higher_channels):
    global streamer, output_frame, filtered_frame
    vs = VideoStream(src=0).start()
    time.sleep(2.0)
    streamer = CVClient(server_addr, lower_channels, higher_channels)
    streamer.setup()
    sio.sleep(2.0)
    # loop detection
    i = 0
    while True:
        time.sleep(0.5)
        frame = vs.read()
        frame = imutils.resize(frame, width=650)

        output_frame = frame.copy()
        filtered_frame = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2HSV)
        streamer.send_video_feed(output_frame, 'cvimage2server')

        if i % 5 == 0:
            masked = cv2.inRange(filtered_frame, np.array(streamer.lower_channels), np.array(streamer.higher_channels))
            streamer.send_video_feed(masked, 'cvfiltered2server')
        i += 1
        if streamer.check_exit():
            streamer.close()
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MQP Dashboard Video Streamer')
    parser.add_argument(
            '--server-addr',  type=str, default='ai-car.herokuapp.com',
            help='The IP address or hostname of the SocketIO server.')
    parser.add_argument("--lowerArr", help="Lower Color Channel", default=[255, 255, 255])
    parser.add_argument("--higherArr", help="Higher Color Channel", default=[0, 0, 0])
    args = parser.parse_args()
    main(args.server_addr, args.lowerArr, args.higherArr)
