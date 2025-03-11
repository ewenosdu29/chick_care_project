import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QMenu, QMenuBar, QPushButton
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtCore import Qt
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialisation de la fenêtre
        self.setWindowTitle('Chick & Care Project')
        self.setGeometry(100, 100, 500, 400)

        icon_path = "D:/ISEN/M1/ProjetM1/chick_care_v2_eh_lp/assets/img/poussin-logo.png"

        # Charger l'image avec QPixmap
        pixmap = QPixmap(icon_path)
        if pixmap.isNull():
            print("❌ Erreur : Impossible de charger l'image avec QPixmap")
        else:
            print("✅ Image chargée avec succès")

            # Appliquer l'icône à la fenêtre
            self.setWindowIcon(QIcon(pixmap))

        # Appliquer le style CSS
        self.setStyleSheet("""
            QMainWindow {
                background-color: #47302b;
            }
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ECEFF4;
            }
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                color: white;
                background-color: #fbffac;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #f9ff84;
            }
            QMenuBar {
                background-color: #3b2723;
                color: #ECEFF4;
            }
        """)

        # Création du widget central et du layout principal
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Affichage de la page d'accueil
        self.show_home_page()

        # Création de la barre de menu
        self.create_menu()

    def create_menu(self):
        """ Crée la barre de menu avec l'option 'Fichier' """
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('Fichier')
        camera = menu_bar.addMenu('Caméra')
        quit_action = QAction('Quitter', self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def show_home_page(self):
        """ Affiche la page d'accueil """
        self.clear_layout()

        self.label = QLabel('Chick & Care Project', self)
        self.label.setAlignment(Qt.AlignCenter)

        self.enter_button = QPushButton("Entrer")
        self.enter_button.setFixedSize(150, 40)
        self.enter_button.clicked.connect(self.show_main_page)  # Affiche la page principale
        self.enter_button.setStyleSheet("color: black;")

        self.labelFooter = QLabel('Développé par : Piment Léonie & Helary Ewen', self)
        self.labelFooter.setAlignment(Qt.AlignCenter)
        self.labelFooter.setStyleSheet("font-size: 12px;")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.enter_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.labelFooter)

    def show_main_page(self):
        """ Affiche la page principale après avoir cliqué sur 'Entrer' """
        self.clear_layout()

        self.label_main = QLabel("Flux en direct de la caméra thermique", self)
        self.label_main.setAlignment(Qt.AlignCenter)

        self.back_button = QPushButton("Retour")
        self.back_button.setFixedSize(150, 40)
        self.back_button.clicked.connect(self.show_home_page)  # Retour à la page d'accueil

        self.layout.addWidget(self.label_main)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

    def clear_layout(self):
        """ Supprime tous les widgets du layout """
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
