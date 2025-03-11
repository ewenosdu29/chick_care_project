import cv2
import time

class Camera:
    def __init__(self, rtsp_urls, fps):
        self.rtsp_urls = rtsp_urls
        self.capture = None
        self.rtsp_url = None
        self.FPS = 1/fps  # Définir le FPS pour la caméra
        self.FPS_MS = int(1000 * self.FPS)  # Convertir en millisecondes par frame
        
        # Tester les différentes URL jusqu'à en trouver une qui fonctionne
        for url in self.rtsp_urls:
            cap = cv2.VideoCapture(url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)  # Réduction de la latence
            
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:  # Vérifier si une frame est capturée
                    self.capture = cap
                    self.rtsp_url = url 
                    print(f"Connexion réussie à la caméra : {url}")
                    break
                else:
                    print(f"Flux non lisible à : {url}")
            else:
                print(f"Échec de connexion à : {url}")
            cap.release()

        self.original_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Résolution capturée : {self.original_width}x{self.original_height}")

    def read_frame(self, target_height=None):
        ret, frame = self.capture.read()
        if not ret:
            print(f"Erreur lors de la lecture du flux vidéo en direct de {self.rtsp_url}")
            
        if cv2.waitKey(1000*camera1.FPS_MS) & 0xFF == ord(' '):  # Quitter si 'espace' est pressé
            break

        else:
            if target_height is not None:
                # Calculer le ratio pour conserver les proportions
                scale = target_height / self.original_height
                new_width = int(self.original_width * scale)
                frame = cv2.resize(frame, (new_width, target_height))
        return ret, frame

    def crop_frame(self, frame, top_percent=0.2, bottom_percent=0.2):
        # Rognage de l'image en haut et en bas.
        height, width, _ = frame.shape
        top = int(height * top_percent)
        bottom = int(height * (1 - bottom_percent))
        return frame[top:bottom, :]

    def release(self):
        self.capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    # FPS différents pour chaque caméra
    fps1 = 340  # FPS pour la caméra 1
    fps2 = 250  # FPS pour la caméra 2
    
    rtsp_urls1 = ["rtsp://admin:vision29@169.254.77.146/Streaming/channels/101", 
                "rtsp://admin:vision29@169.254.27.214/Streaming/channels/101"]
    rtsp_urls2 = ["rtsp://admin:vision29@169.254.77.146/Streaming/channels/201", 
                "rtsp://admin:vision29@169.254.27.214/Streaming/channels/201"]

    camera1 = Camera(rtsp_urls1, fps1)
    camera2 = Camera(rtsp_urls2, fps2)

    while True:
        # Lire les frames des deux caméras
        ret1, frame1 = camera1.read_frame()
        ret2, frame2 = camera2.read_frame(target_height=camera1.original_height)

        if not ret1 or not ret2:
            break

        # Redimensionner frame1 pour qu'elle ait la même taille que frame2
        frame1 = cv2.resize(frame1, (frame2.shape[1], frame2.shape[0]))

        # Vérification des canaux et des types
        if frame1.shape[2] != frame2.shape[2]:  # Si le nombre de canaux diffère
            # Convertir les deux frames en RGB
            frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)

        # Combiner les frames horizontalement
        combined_frame = cv2.hconcat([frame1, frame2])

        # Afficher la frame combinée
        cv2.imshow("Camera 1 and Camera 2", combined_frame)


    camera1.release()
    camera2.release()
