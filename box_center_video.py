import cv2
from ultralytics import YOLO


model = YOLO("yolov8_poussin.pt")

rgb_video_path = "D:/ISEN/M1/ProjetM1/video_elevage/elevage2/video_RGB/output_29-03-2025_18-04-051.mp4"
therm_video_path = "D:/ISEN/M1/ProjetM1/video_elevage/elevage2/video_therm/output_29-03-2025_18-04-052.mp4"
cap_rgb = cv2.VideoCapture(rgb_video_path)
cap_therm = cv2.VideoCapture(therm_video_path)

if not cap_rgb.isOpened():
    print("❌ Impossible d'ouvrir la vidéo en RGB.")
    exit()
if not cap_therm.isOpened():
    print("❌ Impossible d'ouvrir la vidéo en Thermique.")
    exit()

frame_count = 0  # Pour suivre le nombre de frames
detect_every_n_frames = 1  # Exécuter YOLO 1 fois toutes les 5 frames

while cap_rgb.isOpened():
    ret_rgb, frame_rgb = cap_rgb.read()
    ret_therm, frame_therm = cap_therm.read()
    if not ret_rgb:
        print("✅ Fin de la vidéo ou erreur de lecture")
        break
    if not ret_therm:
        print("✅ Fin de la vidéo ou erreur de lecture")
        break

    # Convertir en niveaux de gris
    gray = cv2.cvtColor(frame_therm, cv2.COLOR_BGR2GRAY)
    # Appliquer une colormap
    thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

    # Exécuter YOLO seulement toutes les `n` frames
    if frame_count % detect_every_n_frames == 0:
        results = model(frame_rgb)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                cv2.rectangle(frame_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                # Calcul du centre
                x_moy = (x1 + x2) / 2
                y_moy = (y1 + y2) / 2

                x_moy = max(0, min(int(x_moy), gray.shape[1] - 1))
                y_moy = max(0, min(int(y_moy), gray.shape[0] - 1))

                pixel_value = gray[int(y_moy), int(x_moy)]

                min_temp=20
                max_temp=40

                temp_celsuis = min_temp + (pixel_value / 255) * (max_temp - min_temp)

                print(f"Point de chaleur: x={x_moy}, y={y_moy}")
                cv2.circle(frame_rgb, (int(x_moy), int(y_moy)), 5, (0, 0, 255), -1)
                cv2.putText(frame_rgb, f"{temp_celsuis:.1f} C", (int(x_moy) + 10, int(y_moy) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.imshow("Poussins détectés", frame_rgb)
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

    frame_count += 1  

cap_rgb.release()
cv2.destroyAllWindows()
