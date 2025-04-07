from ultralytics import YOLO

dataset_yaml = "/Users/leoniepiment/Documents/M1ISEN/Projet/chick_care_project/ia/Chick-Care_V2/data.yaml"

model = YOLO('yolov8s.yaml')

model.train(data=dataset_yaml, epochs=1, imgsz=800, conf=0.5, lr0=0.01, lrf=0.1, momentum=0.937, weight_decay=0.0005, augment=True)