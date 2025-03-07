import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QMenu, QMenuBar, QPushButton
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialisation de la fenêtre
        self.setWindowTitle('Chick & Care Project')
        self.setGeometry(100, 100, 500, 400)

        # Appliquer le style CSS
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E3440;
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
                background-color: #5E81AC;
                border-radius: 10px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QMenuBar {
                background-color: #3B4252;
                color: #ECEFF4;
            }
        """)

        # Création du widget central
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Label du titre
        self.label = QLabel('Chick & Care Project', self)
        self.label.setAlignment(Qt.AlignCenter)

        # Bouton "Entrer"
        self.enter_button = QPushButton("Entrer")
        self.enter_button.setFixedSize(150, 40)  # Taille du bouton
        self.enter_button.clicked.connect(self.on_enter_clicked)  # Connecte l'événement

        # Label du footer (texte en petit)
        self.labelFooter = QLabel('Développé par : Piment Léonie & Helary Ewen', self)
        self.labelFooter.setAlignment(Qt.AlignCenter)
        self.labelFooter.setStyleSheet("font-size: 12px;")  # Texte plus petit

        # Ajout des widgets au layout
        layout.addWidget(self.label)
        layout.addWidget(self.enter_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.labelFooter)

        self.setCentralWidget(central_widget)

        # Création de la barre de menu
        self.create_menu()

    def create_menu(self):
        """ Crée la barre de menu avec l'option 'Fichier' """
        menu_bar = self.menuBar()

        # Création du menu 'Fichier'
        file_menu = menu_bar.addMenu('Fichier')

        # Création de l'action 'Quitter'
        quit_action = QAction('Quitter', self)
        quit_action.triggered.connect(self.close)  # Connecte l'action à la méthode close

        # Ajouter l'action 'Quitter' au menu 'Fichier'
        file_menu.addAction(quit_action)

    def on_enter_clicked(self):
        print("Bouton Entrer cliqué !")  # Ajoute ici le comportement souhaité

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
