import cv2
import time

class Camera(object):
    def __init__(self, rtsp_urls, fps):
        self.rtsp_urls = rtsp_urls
        self.capture = None
        self.rtsp_url = None
        self.FPS = 1 / fps  # Définir une fréquence d'images personnalisée
        self.FPS_MS = int(self.FPS * 1000)  # Convertir en millisecondes
        self.frame = None

        # Tester les différentes URL RTSP jusqu'à ce qu'une connexion fonctionne
        for url in self.rtsp_urls:
            self.capture = cv2.VideoCapture(url)
            if not self.capture.isOpened():
                print(f"Échec de connexion à : {url}")
                continue  # Passer à l'URL suivante si la connexion échoue
            ret, _ = self.capture.read()
            if ret:
                self.rtsp_url = url
                print(f"Connexion réussie à la caméra : {url}")
                break
            else:
                print(f"Flux non lisible à : {url}")
                self.capture.release()  # Libérer la ressource si l'URL ne fonctionne pas

        if self.rtsp_url is None:
            print("Aucune connexion n'a pu être établie.")
            exit()  # Sortie si aucune connexion réussie

        # Obtenir la résolution de la caméra
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Résolution capturée : {width}x{height}")

    def update_video(self):
        while True:
            ret, self.frame = self.capture.read()
            if not ret:
                print("Erreur lors de la lecture du flux vidéo en direct")
                break
            # Afficher la vidéo en direct
            cv2.imshow(f"Flux vidéo - {self.rtsp_url}", self.frame)
            if cv2.waitKey(self.FPS_MS) & 0xFF == ord(' '):  # Quitter si 'espace' est pressé
                break

    def release(self):
        self.capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    # Liste des adresses IP à tester pour les deux caméras
    ip_addresses = [
        "169.254.61.84",
        "169.254.77.146",
        "169.254.27.214"
    ]

    fps_cam1 = 340  # FPS pour la première caméra
    fps_cam2 = 250 # FPS pour la deuxième caméra

    # Créer les URL RTSP pour chaque caméra
    rtsp_urls_cam1 = [f"rtsp://admin:vision29@{ip}/Streaming/channels/101" for ip in ip_addresses]
    rtsp_urls_cam2 = [f"rtsp://admin:vision29@{ip}/Streaming/channels/201" for ip in ip_addresses]


    # Créer les objets Camera pour chaque caméra avec des FPS différents
    camera1 = Camera(rtsp_urls_cam1, fps_cam1)
    camera2 = Camera(rtsp_urls_cam2, fps_cam2)

    # Lancer la lecture des flux pour les deux caméras
    camera1.update_video()
    camera2.update_video()

    # Libérer les ressources des deux caméras
    camera1.release()
    camera2.release()

