import sys
import cv2
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt, QTimer
from ipSearch import find_valid_rtsp_ip


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialisation de la fenêtre
        self.setWindowTitle('Chick & Care Project')
        self.setGeometry(500, 200, 640, 480)  # Taille plus petite

        ip = find_valid_rtsp_ip()

        # Définition des URL RTSP des caméras
        self.rtsp_url =  f"rtsp://admin:vision29@{ip}/Streaming/channels/101"   # Remplace avec ton URL

        # Création du widget central et du layout principal
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Affichage de la page d'accueil
        self.show_home_page()

    def show_home_page(self):
        """ Affiche la page d'accueil """
        self.clear_layout()

        self.label = QLabel('Chick & Care Project', self)
        self.label.setAlignment(Qt.AlignCenter)

        self.enter_button = QPushButton("Entrer")
        self.enter_button.setFixedSize(150, 40)
        self.enter_button.clicked.connect(self.show_main_page)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.enter_button, alignment=Qt.AlignCenter)

    def show_main_page(self):
        """ Affiche la page principale avec le flux vidéo """
        self.clear_layout()

        self.label_main = QLabel("Flux en direct de la caméra thermique", self)
        self.label_main.setAlignment(Qt.AlignCenter)

        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)  # Remplace par la taille que tu veux
        self.video_label.setAlignment(Qt.AlignCenter)


        self.back_button = QPushButton("Retour")
        self.back_button.setFixedSize(150, 40)
        self.back_button.clicked.connect(self.show_home_page)

        self.layout.addWidget(self.label_main)
        self.layout.addWidget(self.video_label)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        # Lancer le flux vidéo
        self.start_video_stream()

    def start_video_stream(self):
        """ Initialise la capture vidéo et démarre la mise à jour d'image """
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            print("❌ Erreur : Impossible d'ouvrir le flux RTSP")
            return

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Met à jour l'image toutes les 30ms (~33 FPS)

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


    def clear_layout(self):
        """ Supprime tous les widgets du layout """
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def closeEvent(self, event):
        """ Arrête la capture vidéo lors de la fermeture de l'application """
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
