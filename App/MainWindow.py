from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from IpSearch import find_valid_rtsp_ip
from Camera_Stream import CameraStream  


class MainWindow(QMainWindow):
    """ Fenêtre principale après connexion """
    def __init__(self, widget_manager):
        super().__init__()
        self.widget_manager = widget_manager  # Gestionnaire de pages

        self.setWindowTitle('Chick & Care Project')
        self.setGeometry(500, 200, 640, 480)

        ip = find_valid_rtsp_ip()
        self.rtsp_url = f"rtsp://admin:vision29@{ip}/Streaming/channels/101"

        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        self.show_main_page()

    def show_main_page(self):
        """ Affiche la page principale avec le flux vidéo """
        self.clear_layout()

        self.label_main = QLabel("Flux en direct de la caméra thermique", self)
        self.label_main.setAlignment(Qt.AlignCenter)

        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)

        self.logout_button = QPushButton("Déconnexion")
        self.logout_button.setFixedSize(150, 40)
        self.logout_button.clicked.connect(self.logout)

        self.layout.addWidget(self.label_main)
        self.layout.addWidget(self.video_label)
        self.layout.addWidget(self.logout_button, alignment=Qt.AlignCenter)

        # Démarrage du flux vidéo
        self.camera_stream = CameraStream(self.rtsp_url, self.video_label)
        self.camera_stream.start()

    def logout(self):
        """ Déconnecte l'utilisateur et revient à la page de connexion """
        self.camera_stream.stop()  # Arrête la vidéo
        self.widget_manager.setCurrentIndex(0)  # Revient à `LoginPage`

    def clear_layout(self):
        """ Supprime tous les widgets du layout """
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def closeEvent(self, event):
        """ Arrête proprement le flux vidéo lors de la fermeture """
        if hasattr(self, 'camera_stream'):
            self.camera_stream.stop()
        event.accept()
