from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QComboBox, QCheckBox,  QLineEdit
from PySide6.QtCore import Qt
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from IpSearch import find_valid_rtsp_ip
from Camera_Stream import ChickTemperatureViewer
from Visualisation import Visualisation
from Statistiques import save_statistiques


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

        self.label_main = QLabel("Flux en direct de la caméra")
        self.label_main.setAlignment(Qt.AlignCenter)

        self.video_label = QLabel()
        self.video_label.setFixedSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)

        self.camera_selector = QComboBox()
        ip = find_valid_rtsp_ip()
        self.camera_selector.addItem("Détection des poussins (RGB + Thermique)", {"rgb": f"rtsp://admin:vision29@{ip}/Streaming/channels/101", "therm": f"rtsp://admin:vision29@{ip}/Streaming/channels/201"})
        self.camera_selector.addItem("Caméra Thermique seule", {"therm": f"rtsp://admin:vision29@{ip}/Streaming/channels/201"})

        model_path = "../runs/detect/train2/weights/best.pt"
        self.camera_stream = ChickTemperatureViewer(self.video_label, model_path)

        self.activate_button = QPushButton("Activer la caméra")
        self.stop_button = QPushButton("Arrêter la caméra")

        self.activate_button.clicked.connect(self.activate_selected)
        self.stop_button.clicked.connect(self.stop_camera)

        layout.addWidget(self.label_main)
        layout.addWidget(self.camera_selector)
        layout.addWidget(self.activate_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.video_label)

        return page


    def activate_selected(self):
        # Récupérer l'élément sélectionné dans la ComboBox
        selected_item = self.camera_selector.currentData()

        # Vérifier si les clés 'rgb' et 'therm' sont présentes dans le dictionnaire
        if "rgb" in selected_item and "therm" in selected_item:
            # Si les deux flux sont disponibles, lancer la détection des poussins (RGB + Thermique)
            self.camera_stream.start(selected_item["rgb"], selected_item["therm"])
        elif "therm" in selected_item:
            # Si seule la caméra thermique est sélectionnée, lancer uniquement le flux thermique
            self.camera_stream.start_thermal_only(selected_item["therm"])


    def stop_camera(self):
        self.camera_stream.stop()

    def logout(self):
        """ Déconnecte et retourne à la page de login """
        self.camera_stream.stop()
        self.widget_manager.setCurrentIndex(0)

    def create_visualisation_page(self):
        return Visualisation()

    def create_statistique_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        label = QLabel("Page de statistiques")
        label.setAlignment(Qt.AlignCenter)

        # Champ pour entrer le nombre de poussins
        self.poussins_input = QLineEdit()
        self.poussins_input.setPlaceholderText("Entrez le nombre de poussins")

        # Affichage de la date du jour
        self.date_label = QLabel(f"Date : {datetime.datetime.now().strftime('%Y-%m-%d')}")
        self.date_label.setAlignment(Qt.AlignCenter)

        # Bouton pour enregistrer les données
        self.save_button = QPushButton("Enregistrer")
        self.save_button.clicked.connect(self.save_statistiques)

        # Bouton pour afficher le graphique
        self.show_graph_button = QPushButton("Afficher le graphique")
        self.show_graph_button.clicked.connect(self.show_graph)

        # Ajout des widgets au layout
        layout.addWidget(label)
        layout.addWidget(self.date_label)
        layout.addWidget(self.poussins_input)
        layout.addWidget(self.save_button)
        layout.addWidget(self.show_graph_button)

        # Zone pour afficher le graphique
        self.graph_layout = QVBoxLayout()
        layout.addLayout(self.graph_layout)

        return page

    def save_statistiques(self):
        # Récupérer le nombre de poussins et vérifier que c'est un nombre valide
        try:
            poussins_count = int(self.poussins_input.text())
        except ValueError:
            print("Veuillez entrer un nombre valide de poussins.")
            return
        
        # Récupérer la date du jour
        date_today = self.date_label.text().replace("Date : ", "")

        # Appeler la fonction importée pour enregistrer les statistiques
        save_statistiques(poussins_count, date_today)

        # Optionnel : vider le champ de saisie
        self.poussins_input.clear()

    def show_graph(self):
        # Lire les données enregistrées depuis le fichier
        dates = []
        poussins_counts = []

        try:
            with open("statistiques.txt", "r") as file:
                lines = file.readlines()
                for line in lines:
                    date, count = line.strip().split(", ")
                    dates.append(date)
                    poussins_counts.append(int(count))
        except FileNotFoundError:
            print("Le fichier de statistiques n'existe pas encore.")
            return

        # Créer un graphique avec Matplotlib
        fig, ax = plt.subplots(figsize=(8, 6))

        # Ploter les données
        ax.plot(dates, poussins_counts, marker='o', color='b', linestyle='-', label="Nombre de poussins")
        ax.set_title("Évolution du nombre de poussins")
        ax.set_xlabel("Date")
        ax.set_ylabel("Nombre de poussins")

        # Définir les positions des ticks sur l'axe X
        ax.set_xticks(dates)  # Définir les positions des ticks à chaque date
        ax.set_xticklabels(dates, rotation=45, ha="right")  # Rotation des labels des dates

        ax.legend()

        # Rendre le fond transparent
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')  # Le fond de l'axe également transparent

        # Créer un canvas Matplotlib pour l'affichage dans le widget Qt
        canvas = FigureCanvas(fig)
        canvas.draw()

        # Supprimer le graphique existant avant d'ajouter le nouveau
        if hasattr(self, 'graph_widget'):
            self.graph_widget.deleteLater()

        # Ajouter le canvas au layout Qt
        self.graph_widget = QWidget(self)
        graph_layout = QVBoxLayout(self.graph_widget)
        graph_layout.addWidget(canvas)
        self.graph_layout.addWidget(self.graph_widget)

        # Fermer la figure pour libérer la mémoire
        plt.close(fig)

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




