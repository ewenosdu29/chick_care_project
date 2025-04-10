import sys
import cv2
import threading
import numpy as np
from ultralytics import YOLO
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout 
from PySide6.QtGui import QImage, QPixmap, Qt
from PySide6.QtCore import QTimer


class ChickTemperatureViewer:
    def __init__(self, display_label, model_path):
        self.label = display_label
        self.model = YOLO(model_path)
        self.running = False

    def start(self, rgb_url, therm_url):
        self.cap_rgb = cv2.VideoCapture(rgb_url)
        self.cap_therm = cv2.VideoCapture(therm_url)

        if not self.cap_rgb.isOpened() or not self.cap_therm.isOpened():
            print("❌ Impossible d'ouvrir un des flux.")
            return

        self.rgb_width = int(self.cap_rgb.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.rgb_height = int(self.cap_rgb.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.therm_width = int(self.cap_therm.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.therm_height = int(self.cap_therm.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.scale_x = self.therm_width / self.rgb_width
        self.scale_y = self.therm_height / self.rgb_height

        self.running = True
        self.current_rgb = None
        self.current_therm = None

        threading.Thread(target=self.read_rgb, daemon=True).start()
        threading.Thread(target=self.read_therm, daemon=True).start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(100)

    def start_thermal_only(self, therm_url):
        self.cap_therm = cv2.VideoCapture(therm_url)

        if not self.cap_therm.isOpened():
            print("❌ Impossible d'ouvrir le flux thermique.")
            return

        self.therm_width = int(self.cap_therm.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.therm_height = int(self.cap_therm.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.running = True
        self.current_therm = None

        threading.Thread(target=self.read_therm, daemon=True).start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_thermal_frame)
        self.timer.start(100)

    def read_rgb(self):
        while self.running:
            ret, frame = self.cap_rgb.read()
            if ret:
                self.current_rgb = frame

    def read_therm(self):
        while self.running:
            ret, frame = self.cap_therm.read()
            if ret:
                self.current_therm = frame

    def update_frame(self):
        if self.current_rgb is None or self.current_therm is None:
            return

        frame_rgb = self.current_rgb.copy()
        frame_therm = self.current_therm.copy()
        gray_therm = cv2.cvtColor(frame_therm, cv2.COLOR_BGR2GRAY)

        results = self.model.predict(frame_rgb, verbose=False)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                x_moy_rgb = (x1 + x2) / 2
                y_moy_rgb = (y1 + y2) / 2
                x_moy_therm = int(x_moy_rgb * self.scale_x)
                y_moy_therm = int(y_moy_rgb * self.scale_y)

                temp_color = (0, 255, 0)

                if 0 <= x_moy_therm < self.therm_width and 0 <= y_moy_therm < self.therm_height:
                    pixel_value = gray_therm[y_moy_therm, x_moy_therm]
                    temp_c = 30 + (pixel_value / 255) * (45 - 30)

                    if temp_c < 26.5:
                        temp_color = (0, 0, 255)

                    cv2.putText(frame_rgb, f"{temp_c:.1f}°C", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    cv2.circle(frame_rgb, (int(x_moy_rgb), int(y_moy_rgb)), 5, temp_color, -1)

                cv2.rectangle(frame_rgb, (x1, y1), (x2, y2), temp_color, 2)

        # Redimensionner l'image RGB pour s'adapter au QLabel sans distorsion
        label_width = self.label.width()
        label_height = self.label.height()

        # Calcul du ratio d'aspect pour redimensionner tout en préservant les proportions
        h, w, _ = frame_rgb.shape
        aspect_ratio = w / h
        if label_width / label_height > aspect_ratio:
            new_width = int(label_height * aspect_ratio)
            new_height = label_height
        else:
            new_width = label_width
            new_height = int(label_width / aspect_ratio)
        
        resized_rgb = cv2.resize(frame_rgb, (new_width, new_height))

        rgb_display = cv2.cvtColor(resized_rgb, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_display.shape
        qt_image = QImage(rgb_display.data, w, h, ch * w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_image))

    def update_thermal_frame(self):
        if self.current_therm is None:
            return

        frame_therm = self.current_therm.copy()
        gray_therm = cv2.cvtColor(frame_therm, cv2.COLOR_BGR2GRAY)

        # Appliquer la même échelle de température que précédemment
        temp_color = (0, 255, 0)

        h, w = gray_therm.shape
        for y in range(0, h, 5):  # Parcourir chaque pixel à un intervalle
            for x in range(0, w, 5):
                pixel_value = gray_therm[y, x]
                temp_c = 30 + (pixel_value / 255) * (45 - 30)

                if temp_c < 26.5:
                    temp_color = (0, 0, 255)

                cv2.circle(frame_therm, (x, y), 1, temp_color, -1)

        # Redimensionner l'image thermique pour s'adapter au QLabel sans distorsion
        label_width = self.label.width()
        label_height = self.label.height()

        # Calcul du ratio d'aspect pour redimensionner tout en préservant les proportions
        aspect_ratio = w / h
        if label_width / label_height > aspect_ratio:
            new_width = int(label_height * aspect_ratio)
            new_height = label_height
        else:
            new_width = label_width
            new_height = int(label_width / aspect_ratio)

        # Redimensionner l'image thermique
        resized_therm = cv2.resize(frame_therm, (new_width, new_height))

        therm_display = cv2.cvtColor(resized_therm, cv2.COLOR_BGR2RGB)
        h, w, ch = therm_display.shape
        qt_image = QImage(therm_display.data, w, h, ch * w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_image))


    def stop(self):
        self.running = False
        if hasattr(self, 'cap_rgb'):
            self.cap_rgb.release()
        if hasattr(self, 'cap_therm'):
            self.cap_therm.release()
        self.label.clear()
