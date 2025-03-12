import cv2
import time

class RTSPStreamer:
    def __init__(self, rtsp_url, desired_fps, output_filename):
        """
        Initialise la classe avec l'URL RTSP de la caméra, le FPS souhaité et le nom du fichier de sortie.
        """
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(self.rtsp_url)

        if not self.cap.isOpened():
            print("Erreur : Impossible d'ouvrir le flux RTSP")
            self.cap.release()
            exit()

        # Récupère les FPS d'origine du flux vidéo
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        print(f"FPS d'origine du flux vidéo : {self.fps}")
        
        # FPS souhaité
        self.desired_fps = desired_fps
        print(f"FPS modifié souhaité : {self.desired_fps}")

        # Récupérer la résolution du flux (largeur et hauteur)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Configurer le VideoWriter pour l'enregistrement
        fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec XVID pour .avi
        self.out = cv2.VideoWriter(output_filename, fourcc, self.desired_fps, 
                                    (self.frame_width, self.frame_height))
        print(f"Enregistrement en cours dans : {output_filename}")

    def display_and_record_stream(self):
        """
        Affiche le flux vidéo en temps réel et enregistre dans un fichier.
        """
        prev_frame_time = 0  # Temps précédent (initialement zéro)

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Erreur : Impossible de lire la frame")
                break

            # Temps actuel
            new_frame_time = time.time()

            # Calcul de l'intervalle entre les frames
            time_diff = new_frame_time - prev_frame_time

            # Si l'intervalle est plus grand que 1/fps souhaité, on affiche et enregistre la frame
            if time_diff > 1.0 / self.desired_fps:
                prev_frame_time = new_frame_time  # Mise à jour du temps précédent
                cv2.imshow("Flux RTSP", frame)  # Afficher la frame
                self.out.write(frame)  # Enregistrer la frame dans le fichier

            # Quitter avec la touche 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def release(self):
        """
        Libère les ressources utilisées par la capture vidéo et l'écriture du fichier.
        """
        self.cap.release()
        self.out.release()  # Libération du VideoWriter
        cv2.destroyAllWindows()

# Exemple d'utilisation
if __name__ == "__main__":
    rtsp_url = "rtsp://admin:vision29@169.254.77.146/Streaming/channels/201"  # Remplacez par l'URL RTSP de votre caméra
    output_filename = "recorded_video/output_video.mp4"  # Nom du fichier de sortie

    # Crée l'objet RTSPStreamer avec un FPS souhaité (par exemple, 15 FPS)
    streamer = RTSPStreamer(rtsp_url, desired_fps=30, output_filename=output_filename)

    # Affiche et enregistre le flux en temps réel
    streamer.display_and_record_stream()

    # Libère les ressources à la fin
    streamer.release()
