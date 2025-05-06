from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QHBoxLayout, QScrollArea
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import os
import cv2
import time
from ultralytics import YOLO


class Visualisation(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.update_file_list("RGB")

        # Charger le modèle YOLO
        self.model = YOLO("App/yolov8s_poussin.pt")

        # Timer pour le traitement de la vidéo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.play_video)

        self.is_paused = False  # Variable de contrôle de la pause
        self.is_playing = False  # État de la vidéo
        self.thermal_cap = None  # Initialiser la variable pour la vidéo thermique
        self.temperatures = []
        self.last_avg_time = time.time()
        self.previous_avg_temp = None

    def init_ui(self):
        """Initialisation de l'interface utilisateur"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Contenu scrollable
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # Titre
        self.title_label = QLabel("Page de Visualisation", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; color: white;")
        layout.addWidget(self.title_label)

        # Menu déroulant RGB / Thermique
        self.combo_source = QComboBox(self)
        self.combo_source.addItems(["RGB", "Thermique"])
        self.combo_source.currentTextChanged.connect(self.update_file_list)
        layout.addWidget(self.combo_source)

        # Checkbox IA
        self.ia_checkbox = QCheckBox("Appliquer le modèle IA", self)
        self.ia_checkbox.setEnabled(False)
        layout.addWidget(self.ia_checkbox)

        # Sélection de fichiers
        self.combo_file = QComboBox(self)
        layout.addWidget(self.combo_file)

        # Zone vidéo
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label)

        # Boutons
        button_layout = QHBoxLayout()
        self.launch_button = QPushButton("Lancer la vidéo", self)
        self.launch_button.clicked.connect(self.start_video)
        button_layout.addWidget(self.launch_button)

        self.pause_button = QPushButton("Pause", self)
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.toggle_pause)
        button_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("Arrêter", self)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_video)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        # Température moyenne
        self.avg_temp_label = QLabel("Température moyenne : -- °C", self)
        self.avg_temp_label.setAlignment(Qt.AlignCenter)
        self.avg_temp_label.setStyleSheet("font-size: 16px; color: white;")
        layout.addWidget(self.avg_temp_label)

        # Flèche d’évolution de la température
        self.temp_trend_label = QLabel("", self)
        self.temp_trend_label.setAlignment(Qt.AlignCenter)
        self.temp_trend_label.setStyleSheet("font-size: 20px; color: white;")
        layout.addWidget(self.temp_trend_label)

        # Graphique matplotlib (ajouté dynamiquement dans le code)
        self.create_temp_graph()
        layout.addWidget(self.canvas)

        # ScrollArea configuration
        scroll.setWidget(content_widget)

        # Layout principal de la page
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

        self.setMinimumSize(800, 600)

    def update_file_list(self, source_type):
        """Met à jour les actions selon la sélection de la source (RGB ou Thermique)"""
        if source_type == "RGB":
            # On peut activer le modèle IA pour RGB
            self.update_rgb_files()
            self.ia_checkbox.setEnabled(True)
            self.ia_checkbox.setVisible(True)
        else:
            self.update_therm_files()
            self.ia_checkbox.setVisible(False)

    def update_rgb_files(self):
        """Charge toutes les vidéos RGB dans le combo_file"""
        rgb_folder = "../video_elevage/elevage2/video_RGB"  # Dossier des vidéos RGB
        files = [f for f in os.listdir(rgb_folder) if f.endswith(".mp4")]  # Liste des fichiers .mp4
        
        self.combo_file.clear()  # Clear the combo box before adding new items
        self.combo_file.addItems(files)  # Ajouter les fichiers dans le combo_box

    def update_therm_files(self):
        """Charge toutes les vidéos RGB dans le combo_file"""
        therm_folder = "../video_elevage/elevage2/video_therm"  # Dossier des vidéos RGB
        files = [f for f in os.listdir(therm_folder) if f.endswith(".mp4")]  # Liste des fichiers .mp4
        
        self.combo_file.clear()  # Clear the combo box before adding new items
        self.combo_file.addItems(files)  # Ajouter les fichiers dans le combo_box

    def start_video(self):
        selected_video = self.combo_file.currentText()
        print(f"Vidéo sélectionnée : {selected_video}")

        if selected_video:
            folder = "../video_elevage/elevage2/video_RGB" if self.combo_source.currentText() == "RGB" else "../video_elevage/elevage2/video_therm"
            video_path = os.path.join(folder, selected_video)

            if os.path.exists(video_path):
                self.cap = cv2.VideoCapture(video_path)
                if not self.cap.isOpened():
                    print("Erreur lors de l'ouverture de la vidéo.")
                    return

                # Trouver et ouvrir la vidéo thermique correspondante si la source est RGB
                if self.combo_source.currentText() == "RGB" and self.ia_checkbox.isChecked():
                    matched_paths = find_matching_video_paths(video_path)
                    if matched_paths[1]:
                        self.thermal_cap = cv2.VideoCapture(matched_paths[1])
                        if not self.thermal_cap.isOpened():
                            print("Erreur lors de l'ouverture de la vidéo thermique.")
                            return

                # Activer les boutons pause et arrêter
                self.pause_button.setEnabled(True)
                self.stop_button.setEnabled(True)
                self.is_playing = True
                self.timer.start(30)  # Démarrer la lecture de la vidéo
            else:
                print("❌ Fichier vidéo non trouvé.")
        else:
            print("❌ Aucune vidéo sélectionnée.")

    def toggle_pause(self):
        """Change l'état de pause ou reprise"""
        if self.is_paused:
            # Reprendre la lecture de la vidéo
            self.is_paused = False
            self.timer.start(30)  # Reprendre la lecture
            self.pause_button.setText("Pause")  # Mettre à jour le texte du bouton
        else:
            # Mettre la vidéo en pause
            self.is_paused = True
            self.timer.stop()  # Arrêter la lecture
            self.pause_button.setText("Reprendre")  # Mettre à jour le texte du bouton

    def stop_video(self):
        """Arrête la vidéo et réinitialise l'interface"""
        if hasattr(self, 'cap'):
            self.cap.release()
        if self.thermal_cap:
            self.thermal_cap.release()
        self.timer.stop()
        self.is_playing = False
        self.is_paused = False

        # Réinitialiser le label de la vidéo à un fond noir
        black_image = QImage(640, 480, QImage.Format_RGB888)
        black_image.fill(Qt.black)
        self.video_label.setPixmap(QPixmap.fromImage(black_image))

        # Désactiver les boutons de pause et arrêt
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("Pause")

    def play_video(self):
        if not hasattr(self, 'cap') or not self.cap.isOpened() or self.is_paused:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.cap.release()
            self.timer.stop()
            self.stop_button.setEnabled(False)  # Désactiver le bouton d'arrêt à la fin
            print("🎬 Vidéo terminée.")
            return

        # Si la vidéo thermique est ouverte et que la checkbox IA est cochée, lire la vidéo thermique
        if self.thermal_cap and self.ia_checkbox.isChecked():
            ret_thermal, frame_thermal = self.thermal_cap.read()
            if not ret_thermal:
                print("❌ Impossible de lire la vidéo thermique.")
                return

            # Convertir la vidéo thermique en niveaux de gris pour récupérer la température
            gray = cv2.cvtColor(frame_thermal, cv2.COLOR_BGR2GRAY)

            # Appliquer YOLO sur la frame RGB
            frame = self.apply_yolo_model(frame, gray)

        # Convertir la frame en format RGB pour l'affichage
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, _ = frame.shape
        q_image = QImage(frame.data, width, height, 3 * width, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)

        # Redimensionner le pixmap à 640x480 avant de l'afficher
        scaled_pixmap = pixmap.scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)

    def apply_yolo_model(self, frame, gray):
        """Applique le modèle YOLO à la frame et récupère les températures des poussins"""
        results = self.model(frame)

        rgb_width = frame.shape[1]
        rgb_height = frame.shape[0]

        if self.thermal_cap:
            therm_width = int(self.thermal_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            therm_height = int(self.thermal_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            scale_x = therm_width / rgb_width
            scale_y = therm_height / rgb_height

            frame_temperatures = []

            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    x_moy = (x1 + x2) / 2
                    y_moy = (y1 + y2) / 2

                    x_moy_therm = int(x_moy * scale_x)
                    y_moy_therm = int(y_moy * scale_y)

                    temperature = self.get_temperature_at_point(gray, x_moy_therm, y_moy_therm)
                    frame_temperatures.append(temperature)

                    temp_color = (0, 255, 0)
                    if temperature < 37.5:
                        temp_color = (0, 0, 255)

                    cv2.putText(frame, f"{temperature} C", (int(x_moy) - 10, int(y_moy) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), temp_color, 2)
                    cv2.circle(frame, (int(x_moy), int(y_moy)), 5, (0, 0, 0), -1)

            # Ajouter les températures de cette frame à la liste globale
            self.temperatures.extend(frame_temperatures)

            # Calculer la moyenne toutes les 5 secondes
            current_time = time.time()
            if current_time - self.last_avg_time >= 5 and self.temperatures:
                temps_array = np.array(self.temperatures)
                avg_temp = np.mean(temps_array)
                std_temp = np.std(temps_array)

                # Flèche de variation
                arrow = ""
                if self.previous_avg_temp is not None:
                    if avg_temp > self.previous_avg_temp:
                        arrow = " ↑"
                    elif avg_temp < self.previous_avg_temp:
                        arrow = " ↓"

                self.avg_temp_label.setText(f"Température moyenne : {avg_temp:.2f} °C{arrow}")

                # Met à jour les historiques
                self.temp_history.append(avg_temp)
                self.std_history.append(std_temp)
                self.update_graph()

                self.previous_avg_temp = avg_temp
                self.temperatures.clear()
                self.last_avg_time = current_time

        return frame

    def update_graph(self):
        self.ax.clear()
        self.ax.plot(self.temp_history, label="Température moyenne", color="blue")
        self.ax.fill_between(range(len(self.temp_history)),
                            np.array(self.temp_history) - np.array(self.std_history),
                            np.array(self.temp_history) + np.array(self.std_history),
                            color='blue', alpha=0.2, label="Écart type")

        self.ax.set_ylabel("Température (°C)")
        self.ax.set_xlabel("Mesure")
        self.ax.legend(loc="upper right")
        self.ax.grid(True)
        self.canvas.draw()


    def create_temp_graph(self):
        self.figure = Figure(figsize=(5, 2))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.temp_history = []  # Stocke les moyennes successives
        self.std_history = []   # Stocke les écarts types

    def get_temperature_at_point(self, gray, x, y):
        """Retourne la température à un point donné dans l'image thermique"""
        # Prendre les coordonnées dans l'image thermique pour récupérer la valeur du pixel
        pixel_value = gray[int(y), int(x)]

        # Conversion de la température (exemple 30°C - 45°C)
        min_temp, max_temp = 30, 45  # Plage de température à ajuster selon le matériel
        temp_celsius = min_temp + (pixel_value / 255) * (max_temp - min_temp)
        
        return round(temp_celsius, 2)  # Retourne la température avec deux décimales


def find_matching_video_paths(rgb_path):
    """Trouver la vidéo thermique correspondante pour la vidéo RGB"""
    rgb_path = rgb_path.replace("\\", "/")
    rgb_filename = os.path.basename(rgb_path)
    base_name = "-".join(rgb_filename.split("-")[:3])  # ex: output_29-03-2025_18-04
    base_therm_folder = "../video_elevage/elevage2/video_therm"

    for file in os.listdir(base_therm_folder):
        file_path = os.path.join(base_therm_folder, file).replace("\\", "/")
        if file.startswith(base_name) and file.endswith(".mp4"):
            return [rgb_path, file_path]

    print("❌ Vidéo thermique correspondante non trouvée.")
    return [rgb_path, None]
