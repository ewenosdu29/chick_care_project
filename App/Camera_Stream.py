import cv2
from PySide6.QtCore import QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt, QTimer


class CameraStream:
    """ Gère le flux vidéo RTSP et la mise à jour de l'interface graphique """

    def __init__(self, rtsp_url, video_label):
        self.rtsp_url = rtsp_url
        self.video_label = video_label
        self.cap = None
        self.timer = None

    def start(self):
        """ Initialise la capture vidéo et démarre la mise à jour d'image """
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            print("❌ Erreur : Impossible d'ouvrir le flux RTSP")
            return

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Met à jour toutes les 30ms (~33 FPS)

    def update_frame(self):
        """ Capture et met à jour le QLabel avec la vidéo """
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            qimg = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(qimg)
            pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_label.setPixmap(pixmap)

    def stop(self):
        """ Arrête le flux vidéo proprement """
        if self.timer:
            self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
