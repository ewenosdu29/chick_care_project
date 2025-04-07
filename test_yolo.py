from ultralytics import YOLO
import cv2

# Charger le modèle YOLOv8 avec le fichier .pt
model = YOLO("last.pt")

img_path = "assets\images_poussins\poussin1.jpg"

# Vérifier si l'image est lisible
img = cv2.imread(img_path)
if img is None:
    print("❌ Erreur : Impossible de lire l'image !")
else:
    print("✅ Image chargée correctement")

# Passer le chemin au modèle et non l'image en mémoire
results = model(img_path)


# # Afficher les résultats
for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        print(x1, y1, x2, y2)
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        # Calcul des centres de chaques annotations
        x_moy = (x1 + x2) / 2
        y_moy = (y1 + y2) / 2
        cv2.circle(img, (int(x_moy), int(y_moy)), 5, (0, 0, 255), -1) # dessiner les centres des poussins

cv2.imshow("Poussins détectés", img)
cv2.waitKey(0)
cv2.destroyAllWindows()