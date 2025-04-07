from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget
from PySide6.QtCore import Qt
from IpSearch import find_valid_rtsp_ip
from Camera_Stream import CameraStream


class MainWindow(QMainWindow):
    def __init__(self, widget_manager):
        super().__init__()
        self.widget_manager = widget_manager

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
                font-family: Arial;
                font-size: 16px;
            }
            
            QPushButton {
                background-color: #464545;
                color: white;
                padding: 4px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #676565;
                border: 2px solid #000000;
            }
            
            QPushButton.active-button {
                background-color: #676565;
                border: 2px solid #000000;
            }

            """)

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
        self.button_visualisation = QPushButton("Visualisation")
        self.button_statistique = QPushButton("Statistique")
        self.button_enregistrement = QPushButton("Enregistrement")
        self.button_logout = QPushButton("Déconnexion")

        self.sidebar.addWidget(self.button_home)
        self.sidebar.addWidget(self.button_camera)
        self.sidebar.addWidget(self.button_visualisation)
        self.sidebar.addWidget(self.button_statistique)
        self.sidebar.addWidget(self.button_enregistrement)
        self.sidebar.addStretch()
        self.sidebar.addWidget(self.button_logout)

        # Contenu central avec pages
        self.pages = QStackedWidget()

        self.page_home = self.create_home_page()
        self.page_camera = self.create_camera_page()
        self.page_visualisation = self.create_visualisation_page()
        self.page_statistique = self.create_statistique_page()
        self.page_enregistrement = self.create_enregistrement_page()

        self.pages.addWidget(self.page_home)
        self.pages.addWidget(self.page_camera)
        self.pages.addWidget(self.page_visualisation)
        self.pages.addWidget(self.page_statistique)
        self.pages.addWidget(self.page_enregistrement)

        main_layout.addLayout(self.sidebar)
        main_layout.addWidget(self.pages)

        # Connexion des boutons
        self.button_home.clicked.connect(lambda: (self.pages.setCurrentWidget(self.page_home), self.set_active_button(self.button_home)))
        self.button_camera.clicked.connect(lambda: (self.pages.setCurrentWidget(self.page_camera), self.set_active_button(self.button_camera)))
        self.button_visualisation.clicked.connect(lambda: (self.pages.setCurrentWidget(self.page_visualisation), self.set_active_button(self.button_visualisation)))
        self.button_statistique.clicked.connect(lambda: (self.pages.setCurrentWidget(self.page_statistique), self.set_active_button(self.button_statistique)))
        self.button_enregistrement.clicked.connect(lambda: (self.pages.setCurrentWidget(self.page_enregistrement), self.set_active_button(self.button_enregistrement)))
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
        return page

    def logout(self):
        """ Déconnecte et retourne à la page de login """
        self.camera_stream.stop()
        self.widget_manager.setCurrentIndex(0)

    def create_visualisation_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("Page de visualisation (à compléter)")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page

    def create_statistique_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("Page de statistiques (à compléter)")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page

    def create_enregistrement_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("Page d'enregistrement (à compléter)")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page

    def set_active_button(self, active_button):
        # Supprime la classe active de tous les boutons
        for button in [self.button_home, self.button_camera, self.button_visualisation,
                    self.button_statistique, self.button_enregistrement]:
            button.setProperty("class", "")
            button.setStyleSheet("")  # Force le refresh du style

        # Applique la classe active au bouton sélectionné
        active_button.setProperty("class", "active-button")
        active_button.setStyleSheet("")  # Force le refresh du style

