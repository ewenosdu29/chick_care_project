from ultralytics import YOLO
import cv2

# Charger le modèle YOLOv8 avec le fichier .pt
model = YOLO("yolov8_poussin.pt")

# Définir le chemin de l'image
img_path = "poussin1.png"

# Vérifier si l'image est lisible
img = cv2.imread(img_path)
if img is None:
    print("❌ Erreur : Impossible de lire l'image !")
else:
    print("✅ Image chargée correctement")

# 🔴 Passer le chemin au modèle et non l'image en mémoire
results = model(img_path)

# Afficher les résultats
for result in results:
    result.show()
