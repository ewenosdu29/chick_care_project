import os

def find_matching_video_paths(rgb_path):
    # Normaliser le chemin avec des / pour rester propre
    rgb_path = rgb_path.replace("\\", "/")

    # Extraire juste le nom du fichier (sans dossier)
    rgb_filename = os.path.basename(rgb_path)

    # Trouver le début du nom (jusqu’au dernier tiret pour matcher la therm)
    base_name = "-".join(rgb_filename.split("-")[:3])  # ex: output_29-03-2025_18-04

    # Chemin du dossier où sont stockées les vidéos thermiques
    base_therm_folder = "D:/ISEN/M1/ProjetM1/video_elevage/elevage2/video_therm"

    for file in os.listdir(base_therm_folder):
        file_path = os.path.join(base_therm_folder, file).replace("\\", "/")
        if file.startswith(base_name) and file.endswith(".mp4"):
            return [rgb_path, file_path]

    print("❌ Vidéo thermique correspondante non trouvée.")
    return [rgb_path, None]

# rgb_path = "D:/ISEN/M1/ProjetM1/video_elevage/elevage2/video_RGB/output_29-03-2025_18-04-051.mp4"
# matched_paths = find_matching_video_paths(rgb_path)
# print(matched_paths)

