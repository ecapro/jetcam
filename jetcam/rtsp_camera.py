from .camera import Camera
import atexit
import cv2
import numpy as np
import threading
import traitlets


class RTSPCamera(Camera):
    
    capture_fps = traitlets.Integer(default_value=30)
    capture_width = traitlets.Integer(default_value=640)
    capture_height = traitlets.Integer(default_value=480)   
    capture_device = traitlets.Unicode(default_value="RTSP")
    
    def __init__(self, *args, **kwargs):
        super(RTSPCamera, self).__init__(*args, **kwargs)
        try:
            #self.cap = cv2.VideoCapture(self._gst_str(), cv2.CAP_GSTREAMER)
            self.cap = cv2.VideoCapture(self.__rtsp_pipeline(), cv2.CAP_GSTREAMER)
            #self.cap = cv2.VideoCapture(self.capture_device)
            if not self.cap.isOpened():
                print("Not open CAM:",self.capture_device)
                raise RuntimeError('Could not read image from camera.')
            else:
                print("CAM is opened:",self.capture_device)
            re , image = self.cap.read()
            
            if not re:
                print("Could not read image from camera.")
                raise RuntimeError('Could not read image from camera.')
            
        except:
            print("Could not initialize camera.")
            raise RuntimeError(
                'Could not initialize camera.  Please see error trace.')

        atexit.register(self.cap.release)
                
    def __rtsp_pipeline(self):
        return ('rtspsrc location=%s ! '
                'rtph264depay ! h264parse ! omxh264dec ! '
                'videorate ! videoscale ! '
                'video/x-raw, '
                'width=(int)%d, height=(int)%d, '
                'framerate=(fraction)%d/1 ! '
                'videoconvert ! '
                'video/x-raw, format=BGR ! '
                'appsink' % (self.capture_device, self.capture_width, self.capture_height, self.capture_fps))
    
    def _read(self):
        re, image = self.cap.read()
        if re:
            image_resized = cv2.resize(image,(int(self.width),int(self.height)))
            return image_resized
        else:
            print("Error Cam")
            self.cap.release()
            self.cap = cv2.VideoCapture(self.__rtsp_pipeline(), cv2.CAP_GSTREAMER)
            #self.cap = cv2.VideoCapture(self.capture_device)
            raise RuntimeError('Could not read image from camera')
