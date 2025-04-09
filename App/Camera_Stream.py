import os
import cv2
import shutil
import glob
from ultralytics import YOLO
from PySide6.QtCore import QTimer, Qt, QThread, Signal, QObject
from PySide6.QtGui import QImage, QPixmap


class AIPredictionWorker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, frame, script_dir, model):
        super().__init__()
        self.frame = frame
        self.script_dir = script_dir
        self.model = model

    def run(self):
        try:
            temp_image_path = os.path.join(self.script_dir, 'temp_image.jpg')
            pred_image_path = os.path.join(self.script_dir, 'temp_image_pred.jpg')
            label_txt_path = os.path.join(self.script_dir, 'temp_image_pred.txt')

            # Sauvegarde temporaire
            cv2.imwrite(temp_image_path, cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))

            # Inference
            self.model.predict(temp_image_path, save=True, save_txt=True, imgsz=800, conf=0.3, show_labels=False, show_conf=False)

            # Récupérer le dernier dossier predict
            detect_dir = os.path.join(self.script_dir, 'runs', 'detect')
            predict_folders = sorted(glob.glob(os.path.join(detect_dir, 'predict*')), key=os.path.getmtime, reverse=True)
            if not predict_folders:
                self.error.emit("Aucun dossier 'predict*' trouvé.")
                return

            latest_predict_dir = predict_folders[0]

            # Image annotée
            annotated_image_path = os.path.join(latest_predict_dir, 'temp_image.jpg')
            if os.path.exists(annotated_image_path):
                shutil.copyfile(annotated_image_path, pred_image_path)

            # Label
            label_file = os.path.join(latest_predict_dir, 'labels', 'temp_image.txt')
            if os.path.exists(label_file):
                shutil.copyfile(label_file, label_txt_path)

            # Nettoyage
            shutil.rmtree(latest_predict_dir)

            # Charger image annotée
            annotated_frame = cv2.imread(pred_image_path)
            if annotated_frame is not None:
                annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                self.finished.emit(annotated_frame_rgb)
            else:
                self.finished.emit(self.frame)  # fallback

        except Exception as e:
            self.error.emit(str(e))


class CameraStream:
    def __init__(self, rtsp_url, video_label, ai_enabled=False):
        self.rtsp_url = rtsp_url
        self.video_label = video_label
        self.ai_enabled = ai_enabled
        self.cap = None
        self.timer = None
        self.is_predicting = False
        self.last_annotated_frame = None
        self.script_dir = os.path.dirname(__file__)
        self.model = YOLO(os.path.join(self.script_dir, '../runs/detect/train2/weights/best.pt')) if ai_enabled else None
        self.frame_counter = 0  # Compteur pour limiter le nombre de frames traitées

    def start(self):
        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            print("❌ Erreur : Impossible d'ouvrir le flux RTSP")
            return

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(25)

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("❌ Impossible de lire la frame.")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Limiter les frames traitées (par exemple, afficher toutes les 3 frames)
        if self.frame_counter % 3 == 0:
            if self.ai_enabled and not self.is_predicting:
                self.is_predicting = True
                self.launch_ai_thread(frame_rgb)
                self.display_frame(frame_rgb)  # afficher l’image normale en attendant
            else:
                self.display_frame(frame_rgb)

        self.frame_counter += 1

    def launch_ai_thread(self, frame_rgb):
        self.thread = QThread()
        self.worker = AIPredictionWorker(frame_rgb, self.script_dir, self.model)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_prediction_done)
        self.worker.error.connect(self.on_prediction_error)

        self.thread.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)  # Le thread se supprime après avoir fini son travail
        self.thread.start()

    def on_prediction_done(self, annotated_frame):
        self.last_annotated_frame = annotated_frame
        self.is_predicting = False

    def on_prediction_error(self, error_msg):
        print(f"❌ Erreur IA : {error_msg}")
        self.is_predicting = False

    def display_frame(self, frame_rgb):
        h, w, ch = frame_rgb.shape
        bytes_per_line = 3 * w
        qimg = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(pixmap)

    def stop(self):
        if self.timer:
            self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if hasattr(self, "thread") and self.thread.isRunning():
            self.thread.quit()   # Arrêter le thread
            self.thread.wait()    # Attendre que le thread termine
