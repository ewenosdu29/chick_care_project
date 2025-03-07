import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QMenu, QMenuBar
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
            QMenuBar {
                background-color: #3B4252;
                color: #ECEFF4;
            }
            QMenuBar::item {
                padding: 6px;
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #4C566A;
            }
            QMenu {
                background-color: #4C566A;
                color: #ECEFF4;
                border: 1px solid #81A1C1;
            }
            QMenu::item:selected {
                background-color: #5E81AC;
            }
        """)

        # Création du texte central
        self.label = QLabel('Chick & Care Project', self)
        self.label.setAlignment(Qt.AlignCenter)  

        # Création du widget central
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        central_widget.setLayout(layout)

        # Définir le widget central
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

def main():
    # Créer l'application
    app = QApplication(sys.argv)

    # Créer la fenêtre principale
    window = MainWindow()

    # Afficher la fenêtre
    window.show()

    # Exécuter l'application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
