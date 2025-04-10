import cv2
import threading
import time
from queue import Queue
from ultralytics import YOLO
from App.IpSearch import find_valid_rtsp_ip

# Charger le modèle YOLO
model = YOLO("runs/detect/train2/weights/best.pt")

# Trouver l'IP RTSP
ip = find_valid_rtsp_ip()
if ip is None:
    print("❌ Aucun flux RTSP valide trouvé.")
    exit()

rtsp_url = f"rtsp://admin:vision29@{ip}/Streaming/channels/101"
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("❌ Impossible d'ouvrir le flux RTSP.")
    exit()

print("✅ Flux RTSP ouvert. Appuie sur 'q' pour quitter.")

# === Variables partagées ===
frame_queue = Queue(maxsize=1)
result_frame = None
stop_threads = False

# === Thread lecture de frame ===
def frame_reader():
    global stop_threads
    while not stop_threads:
        ret, frame = cap.read()
        if ret and not frame_queue.full():
            frame_queue.put(frame)

# === Thread YOLO ===
def yolo_worker():
    global result_frame, stop_threads
    while not stop_threads:
        if not frame_queue.empty():
            frame = frame_queue.get()
            resized = cv2.resize(frame, (640, 480))
            results = model(resized, imgsz=640, verbose=False)
            result_frame = results[0].plot()

# === Lancer les threads ===
thread1 = threading.Thread(target=frame_reader)
thread2 = threading.Thread(target=yolo_worker)
thread1.start()
thread2.start()

# === Affichage en boucle principale ===
while True:
    if result_frame is not None:
        cv2.imshow("Flux RTSP avec YOLO - Détection poussins", result_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        stop_threads = True
        break

# === Clean exit ===
thread1.join()
thread2.join()
cap.release()
cv2.destroyAllWindows()
print("🛑 Fermé proprement.")
