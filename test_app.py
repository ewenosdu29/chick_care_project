import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt  # Importation manquante

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Initialisation de la fenêtre
        self.setWindowTitle('Mon Application PySide avec POO')
        self.setGeometry(100, 100, 400, 300)

        # Création du texte à afficher
        self.label = QLabel('Chick & Care Project', self)
        self.label.setAlignment(Qt.AlignCenter)  # Centre le texte

        # Création du layout central
        layout = QVBoxLayout()
        layout.addWidget(self.label)

        # Définir le layout principal de la fenêtre
        self.setLayout(layout)

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
