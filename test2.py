import cv2

class Camera:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.capture = cv2.VideoCapture(self.rtsp_url)
        if not self.capture.isOpened():
            print("Erreur de connexion à la caméra.")
            exit()
        self.FPS = 1 / 300  # Définir une fréquence d'images de 240 FPS
        self.FPS_MS = int(self.FPS * 1000)
        self.frame = None

        self.original_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Résolution capturée : {self.original_width}x{self.original_height}")

    def read_frame(self, target_height=None):
        ret, frame = self.capture.read()
        if not ret:
            print(f"Erreur lors de la lecture du flux vidéo en direct de {self.rtsp_url}")
        else:
            if target_height is not None:
                # Calculer le ratio pour conserver les proportions
                scale = target_height / self.original_height
                new_width = int(self.original_width * scale)
                frame = cv2.resize(frame, (new_width, target_height))
        return ret, frame

    def release(self):
        self.capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    rtsp_url1 = "rtsp://admin:vision29@169.254.61.84/Streaming/channels/201"
    rtsp_url2 = "rtsp://admin:vision29@169.254.61.84/Streaming/channels/101"

    camera1 = Camera(rtsp_url1)
    camera2 = Camera(rtsp_url2)

    while True:
        # Lire les frames des deux caméras
        ret1, frame1 = camera1.read_frame()
        ret2, frame2 = camera2.read_frame(target_height=camera1.original_height)

        if not ret1 or not ret2:
            break

        # Combiner les frames horizontalement
        combined_frame = cv2.hconcat([frame1, frame2])

        # Afficher la frame combinée
        cv2.imshow("Camera 1 and Camera 2", combined_frame)

        if cv2.waitKey(1) & 0xFF == ord(' '):
            break

    camera1.release()
    camera2.release()
