import sys
import os

# Ajouter le chemin du dossier parent au path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from box_center_video import box_center_video

from ultralytics import YOLO

class visualisation:
    def __init__(self, model, video_path, output_path):
        self.model = model
        self.video_path = video_path
        self.output_path = output_path





