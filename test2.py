import cv2
import numpy as np

class Camera:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.capture = cv2.VideoCapture(self.rtsp_url)
        if not self.capture.isOpened():
            print(f"❌ Erreur de connexion à la caméra : {self.rtsp_url}")
            exit()

        # Récupérer la résolution native
        self.original_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"✅ Caméra {self.rtsp_url} - Résolution : {self.original_width}x{self.original_height}")

    def read_frame(self):
        """Lit une frame sans modification"""
        ret, frame = self.capture.read()
        return frame if ret else None

    def release(self):
        self.capture.release()
        cv2.destroyAllWindows()

def pad_frame_to_match(frame, target_height, target_width):
    """Ajoute un fond noir autour de l'image pour l'agrandir sans la déformer"""
    h, w, _ = frame.shape
    top = (target_height - h) // 2
    bottom = target_height - h - top
    left = (target_width - w) // 2
    right = target_width - w - left
    return cv2.copyMakeBorder(frame, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

if __name__ == '__main__':
    rtsp_url1 = "rtsp://admin:vision29@169.254.77.146/Streaming/channels/201"  # 1280x720
    rtsp_url2 = "rtsp://admin:vision29@169.254.77.146/Streaming/channels/101"  # 2688x1520

    camera1 = Camera(rtsp_url1)
    camera2 = Camera(rtsp_url2)

    # Déterminer la plus grande résolution des deux caméras
    max_width = max(camera1.original_width, camera2.original_width)
    max_height = max(camera1.original_height, camera2.original_height)

    while True:
        frame1 = camera1.read_frame()
        frame2 = camera2.read_frame()

        if frame1 is None or frame2 is None:
            break

        # Ajouter des bordures pour égaliser les tailles
        frame1_padded = pad_frame_to_match(frame1, max_height, max_width)
        frame2_padded = pad_frame_to_match(frame2, max_height, max_width)

        # Combiner les frames horizontalement
        combined_frame = np.hstack((frame1_padded, frame2_padded))

        # Afficher la frame combinée
        cv2.imshow("Flux vidéo combiné", combined_frame)

        if cv2.waitKey(1) & 0xFF == ord(' '):  # Quitter avec 'Espace'
            break

    camera1.release()
    camera2.release()
