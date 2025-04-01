import cv2
import numpy as np

'''
_______________________________________________________________________________________________________________________________________________________________________________________
'''

'''
Cette fonction récupère les coordonnées de la souris sur la video et affiche la température pour chaque
endroit où se situe la souris.
'''

def detect_temperature_on_hover(video_path, min_temp=20, max_temp=100):

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir la vidéo.")
        return
    
    mouse_x, mouse_y = 0, 0

    def mouse_callback(event, x, y, flags, param):
        nonlocal mouse_x, mouse_y
        mouse_x, mouse_y = x, y

    cv2.namedWindow("Video Thermique")
    cv2.setMouseCallback("Video Thermique", mouse_callback)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Fin de la vidéo ou erreur de lecture.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

        # Vérifier si la souris est bien sur l'image
        if 0 <= mouse_x < frame.shape[1] and 0 <= mouse_y < frame.shape[0]:
            pixel_value = gray[mouse_y, mouse_x]  # Lire l'intensité du pixel
            temp_celsius = min_temp + (pixel_value / 255) * (max_temp - min_temp)  # Conversion en °C

            cv2.putText(thermal, f"Temp: {temp_celsius:.1f}C", (mouse_x + 10, mouse_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cv2.circle(thermal, (mouse_x, mouse_y), 5, (255, 255, 255), -1)

        cv2.imshow("Video Thermique", thermal)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

'''
_______________________________________________________________________________________________________________________________________________________________________________________
'''

'''
Cette fonction récupère chaque paire de coordonnées (x, y) contenu dans un fichier texte.
En sortie nous avons une liste de coordonnées : [(300,200), (450, 600), ...]
'''
def get_coordinates_from_file(file_path):
    coordinates = []
    try:
        with open(file_path, "r") as file:
            for line in file:
                x, y = map(int, line.strip().split(","))  # Convertit chaque ligne en (x, y)
                coordinates.append((x, y))
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
    return coordinates

'''
_______________________________________________________________________________________________________________________________________________________________________________________
'''

'''
Cette fonction affiche, pour chaque points contenu dans la liste, la température associé au pixel correspondant.
'''
def display_temperatures_from_file(video_path, coord_file, min_temp=20, max_temp=100):

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Erreur : Impossible d'ouvrir la vidéo.")
        return

    coordinates = get_coordinates_from_file(coord_file)
    if not coordinates:
        print("Aucune coordonnée trouvée dans le fichier.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Fin de la vidéo ou erreur de lecture.")
            break

        # Convertir en niveaux de gris
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Appliquer une colormap
        thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

        for (x, y) in coordinates:
            if 0 <= x < frame.shape[1] and 0 <= y < frame.shape[0]:  
                # frame.shape[1] récupère la largeur de l'image en pixel
                # frame.shape[0] récupère la hauteur de l'image en pixel
                pixel_value = gray[y, x]  # Lire l'intensité du pixel (gris)
                temp_celsius = min_temp + (pixel_value / 255) * (max_temp - min_temp)  # Conversion en °C

                cv2.putText(thermal, f"{temp_celsius:.1f} C", (x + 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.circle(thermal, (x, y), 5, (255, 255, 255), -1)

        cv2.imshow("Video Thermique", thermal)
        if cv2.waitKey(25) & 0xFF == ord(' '):
            break

    cap.release()
    cv2.destroyAllWindows()

'''
_______________________________________________________________________________________________________________________________________________________________________________________
'''   

# detect_temperature_on_hover("recorded_video\output_video.avi", min_temp=20, max_temp=40)
display_temperatures_from_file("recorded_video\output_video.avi", "coords.txt", min_temp=20, max_temp=40)