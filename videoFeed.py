# import cv2
# import imutils
#
# class VideoFeed:
#     isInit = None
#
#     def __init__(self):
#         self.isInit = False
#
#     def gen(self):
#         video = cv2.VideoCapture(0)
#         while True:
#             success, image = video.read()
#             image = imutils.resize(image, width=750)
#             ret, jpeg = cv2.imencode('.jpg', image)
#             frame = jpeg.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')