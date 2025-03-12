import cv2
from ipSearch import find_valid_rtsp_ip

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
        print(f"Fichier d'enregistrement : {output_filename}")

    def display_stream(self, record=False):
        """
        Affiche le flux vidéo en temps réel.
        Si 'record' est True, enregistre la vidéo.
        """
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Erreur : Impossible de lire la frame")
                break

            cv2.imshow("Flux RTSP", frame)

            # Si l'enregistrement est activé, on écrit la frame
            if record:
                self.out.write(frame)

            if cv2.waitKey(1) & 0xFF == ord(' '):
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

    ip = find_valid_rtsp_ip()

    if ip:
        print(f"L'IP fonctionnelle est : {ip}")
    else:
        print("Aucune IP RTSP trouvée.")

    rtsp_url = f"rtsp://admin:vision29@{ip}/Streaming/channels/201"  # Remplacez par l'URL RTSP de votre caméra
    print("test :::: :: ",rtsp_url)
    output_filename = "recorded_video/output_video2.avi"  # Nom du fichier de sortie

    print("Bienvenue sur l'afficheur et l'enregistreur de stream RTSP !")
    print("Quelle opération souhaitez-vous réaliser ?")
    print("  - Display the stream (1)")
    print("  - Display & record the stream (2)\n")

    var = int(input("Quel est votre choix ? "))

    fps = int(input("Combien de FPS :"))

    if var == 1:
        rtsp_stream = RTSPStreamer(rtsp_url, fps, output_filename)
        rtsp_stream.display_stream(record=False)  # Ne pas enregistrer
        rtsp_stream.release()
    elif var == 2:
        rtsp_stream = RTSPStreamer(rtsp_url, fps, output_filename)
        rtsp_stream.display_stream(record=True)  # Enregistrer
        rtsp_stream.release()
    else:
        print("Erreur : Choix non valide")