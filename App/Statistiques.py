from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QHBoxLayout, QLineEdit,QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from datetime import datetime
import os

class Statistique(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_last_file()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Titre
        self.title_label = QLabel("Page de Satistique", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; color: white;")
        layout.addWidget(self.title_label)

        button_layout = QHBoxLayout(self)
        # Premier bouton
        self.open_button = QPushButton("Nouvel arrivage", self)
        self.open_button.clicked.connect(self.toggle_arrivage_form)
        button_layout.addWidget(self.open_button)

        # Deuxième bouton
        self.fin_button = QPushButton("Fin", self)
        self.fin_button.clicked.connect(self.close_txt_file)  
        button_layout.addWidget(self.fin_button)

        button_layout.setSpacing(10)
        layout.addLayout(button_layout)

        # --- Formulaire de nouvel arrivage caché au départ ---
        self.arrivage_form = QWidget()
        self.arrivage_form_layout = QVBoxLayout(self.arrivage_form)

        self.nb_poussin = QLineEdit()
        self.nb_poussin.setPlaceholderText("Nombre de poussins")
        self.nb_poussin.setAlignment(Qt.AlignCenter)

        self.race_input = QLineEdit()
        self.race_input.setPlaceholderText("Race des poussins (optionnel)")
        self.race_input.setAlignment(Qt.AlignCenter)

        self.valide_button = QPushButton("Valider", self)
        self.valide_button.clicked.connect(self.create_txt_file)

        self.arrivage_form_layout.addWidget(self.nb_poussin)
        self.arrivage_form_layout.addWidget(self.race_input)
        self.arrivage_form_layout.addWidget(self.valide_button)

        self.arrivage_form.setVisible(False)  # on le cache au début
        layout.addWidget(self.arrivage_form)

        # Champ Nombre de poussins mort de la journée 
        self.num_dead_form = QWidget()
        self.num_dead_form_layout = QHBoxLayout(self.num_dead_form)

        self.dead_poussin = QLineEdit()
        self.dead_poussin.setPlaceholderText("Nombre de poussin mort aujourd'hui")
        self.dead_poussin.setFixedWidth(300)
        self.dead_poussin.setAlignment(Qt.AlignCenter)
        self.num_dead_form_layout.addWidget(self.dead_poussin)

        self.ajout_mort_button = QPushButton("Ajouter la donnée", self)
        self.ajout_mort_button.clicked.connect(self.add_tkt_file)
        self.num_dead_form_layout.addWidget(self.ajout_mort_button)

        layout.addWidget(self.num_dead_form)

        layout.addStretch()
        self.setLayout(layout)

    def create_txt_file(self):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M")
        filename = f"data_{timestamp}.txt"
        filepath = f"fichier_state/{filename}"

        number = self.nb_poussin.text()
        race = self.race_input.text()

        try:
            with open(filepath, 'w') as file:
                file.write(f"Arrivage du {timestamp}\n") 
                file.write(f"Nombre de poussins : {number}\n")
                file.write(f"Race : {race}\n")
                file.write("Données journalières : \n")

            self.current_filename = filepath
            # Écriture dans un fichier persistant
            with open("fichier_state/current.txt", "w") as f:
                f.write(filepath)
            QMessageBox.information(self, "🟢 Fichier ouvert", f"Le fichier a bien été ouvert :\n{filename}")

            self.arrivage_form.setVisible(False)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de créer le fichier : {e}")


    def toggle_arrivage_form(self):
        is_visible = self.arrivage_form.isVisible()
        self.arrivage_form.setVisible(not is_visible)


    def close_txt_file(self):
        if hasattr(self, 'current_filename') and self.current_filename:
            try:
                with open(self.current_filename, 'a') as file:
                    file.write("\n--- Fin du relevé ---\n")
                QMessageBox.information(self, "📦 Fichier clôturé", f"Le fichier a bien été clôturé :\n{self.current_filename}")
                self.current_filename = None  # ✅ désactive les écritures futures
                if os.path.exists("fichier_state/current.txt"):
                    os.remove("fichier_state/current.txt")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Problème à la fermeture : {e}")
        else:
            QMessageBox.warning(self, "Aucun fichier", "Aucun fichier actif à clôturer.")

    def load_last_file(self):
        try:
            with open("fichier_state/current.txt", "r") as f:
                self.current_filename = f.read().strip()
                if os.path.exists(self.current_filename):
                    print(f"✔️ Fichier récupéré : {self.current_filename}")
                else:
                    self.current_filename = None
        except FileNotFoundError:
            self.current_filename = None


    def add_tkt_file(self): 
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d")
        number = self.dead_poussin.text()
        if hasattr(self, 'current_filename') and self.current_filename:
            try:
                with open(self.current_filename, 'a') as file:
                    file.write(f"{timestamp} : {number}\n")
                QMessageBox.information(self, "Ajout de la donnée", f"Ajout de la donnée :\n{self.current_filename}")
                self.dead_poussin.clear()
            except Exception as e:
                print(f"Erreur lors de la clôture : {e}")
        else:
            print("Aucun fichier actif à clôturer.")
