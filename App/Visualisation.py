from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QCheckBox, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
import os
import cv2
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

    def init_ui(self):
        """Initialisation de l'interface utilisateur"""
        layout = QVBoxLayout(self)

        # Titre
        self.title_label = QLabel("Page de Visualisation", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; color: white;")
        
        # Menu déroulant pour sélectionner RGB ou Thermique
        self.combo_source = QComboBox(self)
        self.combo_source.addItem("RGB")
        self.combo_source.addItem("Thermique")
        self.combo_source.currentTextChanged.connect(self.update_file_list)
        
        # Ajouter le titre et le menu déroulant au layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.combo_source)

        # Option pour activer/désactiver l'IA
        self.ia_checkbox = QCheckBox("Appliquer le modèle IA", self)
        self.ia_checkbox.setEnabled(False)  # IA ne peut être activée que pour RGB
        layout.addWidget(self.ia_checkbox)

        self.combo_file = QComboBox(self)
        layout.addWidget(self.combo_file)

        # Zone de lecture vidéo
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)
        self.video_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.video_label)

        # Layout horizontal pour les boutons (Lancer, Pause, Arrêter)
        button_layout = QHBoxLayout()

        # Bouton pour lancer la vidéo
        self.launch_button = QPushButton("Lancer la vidéo", self)
        self.launch_button.clicked.connect(self.start_video)  # Connecter le bouton à une fonction
        button_layout.addWidget(self.launch_button)

        # Bouton pour mettre en pause/reprendre la vidéo
        self.pause_button = QPushButton("Pause", self)
        self.pause_button.setEnabled(False)  # Désactivé tant qu'aucune vidéo n'est en cours
        self.pause_button.clicked.connect(self.toggle_pause)  # Connecter le bouton de pause
        button_layout.addWidget(self.pause_button)

        # Bouton pour arrêter la vidéo
        self.stop_button = QPushButton("Arrêter", self)
        self.stop_button.setEnabled(False)  # Désactivé tant qu'aucune vidéo n'est en cours
        self.stop_button.clicked.connect(self.stop_video)  # Connecter le bouton d'arrêt
        button_layout.addWidget(self.stop_button)

        # Ajouter le layout horizontal des boutons au layout principal
        layout.addLayout(button_layout)

        # Centrer l'interface
        self.setLayout(layout)

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
        """Appliquer YOLO et afficher la température de la vidéo thermique"""
        results = self.model(frame)  # Appliquer le modèle sur l'image

        # Obtenir les dimensions de la vidéo RGB et thermique
        rgb_width = frame.shape[1]  # Largeur de l'image RGB
        rgb_height = frame.shape[0]  # Hauteur de l'image RGB

        if self.thermal_cap:
            therm_width = int(self.thermal_cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Largeur de l'image thermique
            therm_height = int(self.thermal_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # Hauteur de l'image thermique

            # Calcul des facteurs d'échelle
            scale_x = therm_width / rgb_width
            scale_y = therm_height / rgb_height

            # Parcourir les résultats pour chaque détection
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0]

                    x_moy = (x1 + x2) / 2
                    y_moy = (y1 + y2) / 2

                    # Appliquer les facteurs d'échelle pour adapter les coordonnées RGB à la vidéo thermique
                    x_moy_therm = int(x_moy * scale_x)
                    y_moy_therm = int(y_moy * scale_y)

                    # Dessiner un rectangle autour de l'objet détecté
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)  # Rectangle vert
                    cv2.circle(frame, (int(x_moy), int(y_moy)), 5, (0, 0, 0), -1)  # Point noir au centre

                    # Obtenir la température à ces coordonnées (sur l'image thermique)
                    temperature = self.get_temperature_at_point(gray, x_moy_therm, y_moy_therm)

                    # Afficher la température sur l'image RGB
                    cv2.putText(frame, f"{temperature} C", (int(x_moy) - 10, int(y_moy) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2, cv2.LINE_AA)  # Texte jaune

        return frame


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
