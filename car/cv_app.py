import argparse
from imutils.video import VideoStream
import time
import socketio
import base64
import cv2
import imutils
import numpy as np

# for debugging on, use
# sio = socketio.Client(logger=True, engineio_logger=True)
sio = socketio.Client()

@sio.event(namespace='/cv')
def connect():
    print('[INFO] Connected to server.')

@sio.event(namespace='/cv')
def connect_error():
    print('[INFO] Failed to connect to server.')


@sio.event(namespace='/cv')
def disconnect():
    print('[INFO] Disconnected from server.')


@sio.event(namespace='/cv')
def start_car(car_json):
    speed = car_json['speed']
    higher_channels = car_json['higher_channels']
    lower_channels = car_json['lower_channels']
    print('[INFO] Start car script.')


class CVClient(object):
    def __init__(self, server_addr, lower_channels, higher_channels):
        self.server_addr = server_addr
        self.server_port = 5000
        self.lower_channels = lower_channels
        self.higher_channels = higher_channels

    def setup(self):
        print('[INFO] Connecting to server http://{}:{}...'.format(
            self.server_addr, self.server_port))
        sio.connect(
            'http://{}:{}'.format(self.server_addr, self.server_port),
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

    def send_data(self, frame):
        frame = imutils.resize(frame, width=650)
        sio.emit(
            'cv2server',
            {
                'image': self._convert_image_to_jpeg(frame, self.lower_channels, self.higher_channels)
            },
            namespace='/cv'
        )


def main(server_addr, lower_channels, higher_channels):
    vs = VideoStream(src=0).start()
    time.sleep(2.0)
    streamer = CVClient(server_addr, lower_channels, higher_channels)
    streamer.setup()
    sio.sleep(2.0)
    # loop detection
    while True:
        time.sleep(0.1)
        frame = vs.read()
        streamer.send_data(frame)

        if streamer.check_exit():
            streamer.close()
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MQP Dashboard Video Streamer')
    parser.add_argument(
            '--server-addr',  type=str, default='0.0.0.0',
            help='The IP address or hostname of the SocketIO server.')
    parser.add_argument("--lowerArr", help="Lower Color Channel", default=[255, 255, 255])
    parser.add_argument("--higherArr", help="Higher Color Channel", default=[0, 0, 0])
    args = parser.parse_args()
    main(args.server_addr, args.lowerArr, args.higherArr)
