import cv2
import time

class Camera(object):
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.capture = cv2.VideoCapture(self.rtsp_url) # Open the RTSP stream dans une nouvelle fenetre 
        if not self.capture.isOpened():
            print("Erreur de connexion à la caméra.") 
            exit()
        self.FPS = 1 / 200  # Définir une fréquence d'images de 30 FPS
        self.FPS_MS = int(self.FPS * 1000)
        self.frame = None

    def update_video(self):
        while True: 
            ret, self.frame = self.capture.read()
            if not ret:
                print("Erreur lors de la lecture du flux.")
                break
            # Afficher la vidéo en direct
            cv2.imshow("Flux vidéo", self.frame)
            if cv2.waitKey(self.FPS_MS) & 0xFF == ord(' '):  # Quitter si 'q' est pressé
                break
            time.sleep(self.FPS)

    def release(self):
        self.capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    # Adresse RTSP de la caméra
    rtsp_url = "rtsp://admin:vision29@169.254.61.84/Streaming/channels/201"
    camera = Camera(rtsp_url)
    camera.update_video()
    camera.release()
