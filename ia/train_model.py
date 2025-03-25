from ultralytics import YOLO

dataset_yaml = "D:/ISEN/M1/ProjetM1/DATASET/Chick-Care_V2.v1i.yolov8/data.yaml"

model = YOLO('yolov8n.yaml')

model.train(data=dataset_yaml, epochs=1, imgsz=640)