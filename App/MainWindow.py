from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget
from PySide6.QtCore import Qt
from IpSearch import find_valid_rtsp_ip
from Camera_Stream import CameraStream


class MainWindow(QMainWindow):
    def __init__(self, widget_manager):
        super().__init__()
        self.widget_manager = widget_manager

        self.setWindowTitle('Chick & Care Project')
        self.setGeometry(300, 100, 1000, 800)

        # Widgets principaux
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout principal horizontal : menu + contenu
        main_layout = QHBoxLayout(main_widget)

        # Barre latérale de navigation
        self.sidebar = QVBoxLayout()
        self.button_home = QPushButton("Accueil")
        self.button_camera = QPushButton("Caméra")
        self.button_logout = QPushButton("Déconnexion")

        self.sidebar.addWidget(self.button_home)
        self.sidebar.addWidget(self.button_camera)
        self.sidebar.addStretch()
        self.sidebar.addWidget(self.button_logout)

        # Contenu central avec pages
        self.pages = QStackedWidget()

        self.page_home = self.create_home_page()
        self.page_camera = self.create_camera_page()

        self.pages.addWidget(self.page_home)
        self.pages.addWidget(self.page_camera)

        main_layout.addLayout(self.sidebar)
        main_layout.addWidget(self.pages)

        # Connexion des boutons
        self.button_home.clicked.connect(lambda: self.pages.setCurrentWidget(self.page_home))
        self.button_camera.clicked.connect(lambda: self.pages.setCurrentWidget(self.page_camera))
        self.button_logout.clicked.connect(self.logout)

    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("Bienvenue dans Chick & Care !")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page

    def create_camera_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        self.label_main = QLabel("Flux en direct de la caméra thermique")
        self.label_main.setAlignment(Qt.AlignCenter)

        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.label_main)
        layout.addWidget(self.video_label)

        # Lancer le flux caméra
        ip = find_valid_rtsp_ip()
        self.rtsp_url = f"rtsp://admin:vision29@{ip}/Streaming/channels/101"
        self.camera_stream = CameraStream(self.rtsp_url, self.video_label)
        self.camera_stream.start()

        print("Flux OK !")
        return page

    def logout(self):
        """ Déconnecte et retourne à la page de login """
        self.camera_stream.stop()
        self.widget_manager.setCurrentIndex(0)

    def closeEvent(self, event):
        if hasattr(self, 'camera_stream'):
            self.camera_stream.stop()
        event.accept()
