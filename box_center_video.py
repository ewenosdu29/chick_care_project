import cv2
from ultralytics import YOLO

# model = YOLO("D:/ISEN/M1/ProjetM1/chick_care_v2_eh_lp/runs/detect/train9/weights/best.pt")
model = YOLO("yolov8n.pt")

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

rgb_width = int(cap_rgb.get(cv2.CAP_PROP_FRAME_WIDTH))   # 1920
rgb_height = int(cap_rgb.get(cv2.CAP_PROP_FRAME_HEIGHT)) # 1080
therm_width = int(cap_therm.get(cv2.CAP_PROP_FRAME_WIDTH))  # 1280
therm_height = int(cap_therm.get(cv2.CAP_PROP_FRAME_HEIGHT)) # 720

# Facteurs d'échelle pour adapter les coordonnées
scale_x = therm_width / rgb_width
scale_y = therm_height / rgb_height

frame_count = 0  # Compteur de frames
detect_every_n_frames = 1  # Exécuter YOLO toutes les 5 frames

while cap_rgb.isOpened():
    ret_rgb, frame_rgb = cap_rgb.read()
    ret_therm, frame_therm = cap_therm.read()
    
    if not ret_rgb or not ret_therm:
        print("✅ Fin de la vidéo ou erreur de lecture")
        break

    # Convertir en niveaux de gris et appliquer une colormap
    gray = cv2.cvtColor(frame_therm, cv2.COLOR_BGR2GRAY)

    # Exécuter YOLO toutes les `n` frames
    if frame_count % detect_every_n_frames == 0:
        results = model(frame_rgb)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                cv2.rectangle(frame_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2) # rectangle en vert car bonne temperature

                x_moy_rgb, y_moy_rgb = (x1 + x2) / 2, (y1 + y2) / 2

                # Adapter les coordonnées pour la résolution thermique
                x_moy_therm = int(x_moy_rgb * scale_x)
                y_moy_therm = int(y_moy_rgb * scale_y)

                if 0 <= x_moy_therm < therm_width and 0 <= y_moy_therm < therm_height:
                    # Extraire la valeur du pixel
                    pixel_value = gray[y_moy_therm, x_moy_therm]

                    # Conversion de la température (exemple 20°C - 40°C)
                    min_temp, max_temp = 30, 45
                    temp_celsius = min_temp + (pixel_value / 255) * (max_temp - min_temp)

                    if temp_celsius < 26.5: # on verifie si la temperature est anormalement basse 
                        print(f"Atention ! Température de {temp_celsius}°C détectée ! -> position : ({x_moy_therm}, {y_moy_therm})")
                        cv2.rectangle(frame_rgb, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2) # annotations en rouge pour une temp anormale
                        cv2.circle(frame_rgb, (int(x_moy_rgb), int(y_moy_rgb)), 5, (0, 0, 255), -1)
                        cv2.putText(frame_rgb, f"{temp_celsius:.1f} C", (int(x_moy_rgb) + 10, int(y_moy_rgb) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                    print(f"Point de chaleur: ({x_moy_therm}, {y_moy_therm}) → Température: {temp_celsius:.1f}°C")

                    cv2.circle(frame_rgb, (int(x_moy_rgb), int(y_moy_rgb)), 5, (0, 0, 255), -1)
                    cv2.putText(frame_rgb, f"{temp_celsius:.1f} C", (int(x_moy_rgb) + 10, int(y_moy_rgb) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                else:
                    print(f"Poussin hors champ thermique (x={x_moy_rgb}, y={y_moy_rgb})")

    cv2.imshow("Poussins détectés", frame_rgb)
    if cv2.waitKey(1) & 0xFF == ord(' '):
        break

    frame_count += 1  # Incrémenter le compteur de frames

cap_rgb.release()
cap_therm.release()
cv2.destroyAllWindows()
