from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

class LoginPage(QWidget):
    """ Page de connexion """
    def __init__(self, widget_manager):
        super().__init__()
        self.widget_manager = widget_manager

        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                font-size: 16px;
            }
            
            QLabel {
                color: white;
                font-weight: bold;
            }

            QLabel#titleLabel {
                font-size: 28px;
                margin-bottom: 10px;
            }

            QLabel#subtitleLabel {
                color: white;
                font-size: 20px;
            }
            
            QLineEdit {
                padding: 8px;
                border: 2px solid #ccc;
                border-radius: 4px;
                background-color: #464545 ;
                font-size: 18px;
            }
            
            QPushButton {
                background-color: #7da6ff;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 5px;
                margin-top: 10px;
            }
            
            QLabel#error_label {
                color: red;
                font-style: italic;
            }
        """)

        # Layout principal (centrage vertical)
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        # Layout horizontal pour centrer horizontalement le formulaire
        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignCenter)

        # Layout du formulaire (login/pwd/bouton/erreur)
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)

        self.label1 = QLabel("Chick & Care")
        self.label1.setAlignment(Qt.AlignCenter)
        self.label1.setObjectName("titleLabel")

        self.label2= QLabel("Connexion")
        self.label2.setAlignment(Qt.AlignCenter)
        self.label2.setObjectName("subtitleLabel")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Identifiant")
        self.username_input.setFixedWidth(300)
        self.username_input.setAlignment(Qt.AlignCenter)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedWidth(300)
        self.password_input.setAlignment(Qt.AlignCenter)

        self.username_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.check_login)

        self.login_button = QPushButton("Se connecter")
        self.login_button.setFixedWidth(150)
        self.login_button.clicked.connect(self.check_login)

        self.error_label = QLabel("")
        self.error_label.setObjectName("error_label")
        self.error_label.setAlignment(Qt.AlignCenter)

        # Ajout des widgets au layout du formulaire
        form_layout.addWidget(self.label1)
        form_layout.addWidget(self.label2)
        form_layout.addSpacing(10)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        form_layout.addWidget(self.error_label)

        # Centre le formulaire horizontalement
        hbox.addLayout(form_layout)
        # Et ajoute le tout au layout principal (centrage vertical)
        main_layout.addLayout(hbox)

    def check_login(self):
        """ Vérifie les identifiants """
        username = self.username_input.text()
        password = self.password_input.text()

        valid_users = {
            "eleveur1": "password123",
            "admin": "123", 
        }

        if username in valid_users and valid_users[username] == password:
            QMessageBox.information(self, "Succès", "Connexion réussie !")
            self.widget_manager.setCurrentIndex(1)
            self.password_input.clear()
            self.username_input.clear()
        else:
            QMessageBox.warning(self, "Erreur", "Identifiant ou mot de passe incorrect !")
