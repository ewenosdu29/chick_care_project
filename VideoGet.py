from threading import Thread
import cv2

class VideoGet:
    """
    Read frames in dedicated thread
    """
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        (self.status, self.frame) = self.cap.read()
        self.stopped = False

    def start(self):    
        Thread(target=self.get, args=()).start()  # start new thread
        return self
    
    def get(self):
        while not self.stopped:
            if not self.status:
                self.stop()
            else:
                (self.status, self.frame) = self.cap.read()

    def stop(self):
        self.stopped = True

        
        
        
        