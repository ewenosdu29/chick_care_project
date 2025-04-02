from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QMessageBox
from PySide6.QtCore import Qt


class LoginPage(QWidget):
    """ Page de connexion """
    def __init__(self, widget_manager):
        super().__init__()
        self.widget_manager = widget_manager  # Gestionnaire de pages

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Connexion à Chick & Care", self)
        self.label.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Identifiant")
        self.username_input.setAlignment(Qt.AlignCenter)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)  # Masque le mot de passe
        self.password_input.setAlignment(Qt.AlignCenter)

        self.login_button = QPushButton("Se connecter")
        self.login_button.clicked.connect(self.check_login)

        self.error_label = QLabel("", self)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: red;")

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.error_label)

    def check_login(self):
        """ Vérifie les identifiants """
        username = self.username_input.text()
        password = self.password_input.text()

        # Identifiants autorisés (à remplacer par une base de données plus tard)
        valid_users = {
            "eleveur1": "password123",
            "admin": "adminpass"
        }

        if username in valid_users and valid_users[username] == password:
            QMessageBox.information(self, "Succès", "Connexion réussie !")
            self.widget_manager.setCurrentIndex(1)  # Passe à la page principale
        else:
            QMessageBox.warning(self, "Erreur", "Identifiant ou mot de passe incorrect !")
