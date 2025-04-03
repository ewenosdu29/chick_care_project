from ultralytics import YOLO

dataset_yaml = "C:\\Users\\timch\\Documents\\AAACours\\nini\\chick_care_project\\ia\\Base_IA\\Chick-Care_V2\\data.yaml"

model = YOLO('yolov8n.yaml')

model.train(data=dataset_yaml, epochs=100, imgsz=640, conf=0.3)
