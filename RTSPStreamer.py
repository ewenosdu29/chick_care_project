import cv2
import time
import multiprocessing
from datetime import datetime
from ipSearch import find_valid_rtsp_ip

class RTSPStreamer:
    def __init__(self, rtsp_url, desired_fps, output_filename, window_name):
        """
        Initialise la classe avec l'URL RTSP de la caméra, le FPS souhaité, le nom du fichier de sortie et le nom de la fenêtre.
        """
        self.rtsp_url = rtsp_url
        self.window_name = window_name  # Nom unique pour la fenêtre

        self.cap = cv2.VideoCapture(self.rtsp_url)
        if not self.cap.isOpened():
            print(f"Erreur : Impossible d'ouvrir le flux RTSP {self.rtsp_url}")
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
            if self.window_name == "Flux Camera 1":  # Appliquer uniquement sur la caméra 1
                scale_h = 1.3  # Facteur de zoom (1.3 = 130% de la taille d'origine)
                scale_w = 1.55 # Facteur de zoom (1.55 = 155% de la taille d'origine)
                height, width = frame.shape[:2] 
                new_width, new_height = int(width * scale_w), int(height * scale_h)

                # Redimensionner l'image
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

                # Centrage du zoom (recadrer au centre)
                center_x, center_y = new_width // 2, new_height // 2
                start_x, start_y = center_x - width // 2, center_y - height // 2
                frame = frame[start_y:start_y + height, start_x:start_x + width]  # Recadrer

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
                cv2.imshow(self.window_name, frame)  # Afficher la frame avec un nom unique pour chaque fenêtre
                self.out.write(frame)  # Enregistrer la frame dans le fichier

            # Quitter avec la touche 'q'
            if cv2.waitKey(1) & 0xFF == ord(' '):
                break

    def release(self):
        """
        Libère les ressources utilisées par la capture vidéo et l'écriture du fichier.
        """
        self.cap.release()
        self.out.release()  # Libération du VideoWriter
        cv2.destroyWindow(self.window_name)  # Fermer la fenêtre associée à ce thread

# Exemple d'utilisation
def start_stream(rtsp_url, desired_fps, output_filename, window_name, var):
    if var == 1:
        rtsp_stream = RTSPStreamer(rtsp_url, desired_fps, output_filename, window_name)
        rtsp_stream.display_and_record_stream()  # Ne pas enregistrer
        rtsp_stream.release()
    elif var == 2:
        rtsp_stream = RTSPStreamer(rtsp_url, desired_fps, output_filename, window_name)
        rtsp_stream.display_and_record_stream()  # Enregistrer
        rtsp_stream.release()
    else:
        print("Erreur : Choix non valide")

if __name__ == "__main__":

    ip = find_valid_rtsp_ip()
    print(ip)

    if ip:
        print(f"L'IP fonctionnelle est : {ip}")
    else:
        print("Aucune IP RTSP trouvée.")
        
    print("Bienvenue sur l'afficheur et l'enregistreur de stream RTSP !")
    print("Quelle opération souhaitez-vous réaliser ?")
    print("  - Display the stream (1)")
    print("  - Display & record the stream (2)\n")

    var = int(input("Quel est votre choix ? "))

    fps = int(input("Combien de FPS :"))

    rtsp_urls_cam1 = f"rtsp://admin:vision29@{ip}/Streaming/channels/101" 
    rtsp_urls_cam2 = f"rtsp://admin:vision29@{ip}/Streaming/channels/201"

    # Remplacez par l'URL RTSP de votre caméra
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    output_filename1 = f"../Video_test/Elevage_1/video_RGB/output_{timestamp}1.mp4" 
    output_filename2 = f"../Video_test/Elevage_1/video_therm/output_{timestamp}2.mp4" 

    # Créer des processus pour chaque caméra
    process1 = multiprocessing.Process(target=start_stream, args=(rtsp_urls_cam1, fps, output_filename1, "Flux Camera 1", var))
    process2 = multiprocessing.Process(target=start_stream, args=(rtsp_urls_cam2, fps, output_filename2, "Flux Camera 2", var))

    process1.start()
    process2.start()

    process1.join()
    process2.join()
