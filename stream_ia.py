import cv2
import time
from ultralytics import YOLO
from ipSearch import find_valid_rtsp_ip

class RTSPYOLOStreamer:
    def __init__(self, rtsp_url, model_path, desired_fps=300):
        """
        Initialise la classe avec l'URL RTSP de la caméra, le modèle YOLO et le FPS souhaité.
        """
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(self.rtsp_url)

        if not self.cap.isOpened():
            print("❌ Erreur : Impossible d'ouvrir le flux RTSP")
            self.cap.release()
            exit()

        print("✅ Flux RTSP ouvert avec succès.")

        # Charger le modèle YOLO
        self.model = YOLO(model_path)
        print(f"✅ Modèle YOLO chargé : {model_path}")

        # Récupérer les FPS réels de la caméra
        self.original_fps = self.cap.get(cv2.CAP_PROP_FPS)
        print(f"🎥 FPS réel du flux : {self.original_fps:.2f}")

        # Définir le FPS souhaité
        self.desired_fps = desired_fps
        self.frame_delay = 1 / self.desired_fps  # Délai entre les frames

    def display_stream(self):
        """
        Affiche le flux vidéo en temps réel avec détection YOLO.
        """
        last_time = time.time()

        while self.cap.isOpened():
            self.cap.grab()  # Capture une image en arrière-plan pour éviter les blocages
            ret, frame = self.cap.retrieve()  # Récupère l'image capturée
            
            if not ret:
                print("❌ Erreur : Impossible de lire la frame")
                break

            # Appliquer YOLO en mode streaming pour optimiser la vitesse
            results = self.model(frame, stream=True, verbose=False)

            # Dessiner les annotations sur l'image
            for result in results:
                annotated_frame = result.plot()

            # Afficher le flux
            cv2.imshow("Flux RTSP avec YOLO", annotated_frame)

            # Gestion du FPS pour éviter un affichage trop rapide
            elapsed_time = time.time() - last_time
            if elapsed_time < self.frame_delay:
                time.sleep(self.frame_delay - elapsed_time)
            last_time = time.time()

            # Quitter avec ESPACE
            if cv2.waitKey(1) & 0xFF == ord(' '):
                break

    def release(self):
        """
        Libère les ressources utilisées par la capture vidéo.
        """
        self.cap.release()
        cv2.destroyAllWindows()

# Exemple d'utilisation
if __name__ == "__main__":
    ip = find_valid_rtsp_ip()

    if ip:
        print(f"✅ L'IP fonctionnelle est : {ip}")
    else:
        print("❌ Aucune IP RTSP trouvée.")
        exit()

    rtsp_url = f"rtsp://admin:vision29@{ip}/Streaming/channels/101"  # Remplacez par votre URL RTSP
    print(f"🔗 Connexion au flux : {rtsp_url}")

    model_path = "yolov8_poussin.pt"  # Chemin vers le modèle YOLO
    desired_fps = 15  # Modifier selon le besoin

    rtsp_stream = RTSPYOLOStreamer(rtsp_url, model_path, desired_fps)
    rtsp_stream.display_stream()
    rtsp_stream.release()
