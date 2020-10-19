import cv2
import time



class Camera(object):

    def __init__(self, cam_type):
        if not cam_type:
            self.camera = cv2.VideoCapture(0)
        else: self.camera = cv2.VideoCapture(cam_type)


    # generic 'get frame' function
    # any frame from any VideoCapture
    def get_frame(self):
        if not self.camera.isOpened(): raise RuntimeError('Can\'t start camera')
        while True:
            try:
                flag, fr = self.camera.read()
                #time.sleep(0.04)
                #cv2.waitKey(40) # a 25 fps playback rate
                    # encode
                return cv2.imencode('.jpg', fr)[1].tobytes()
            except: continue