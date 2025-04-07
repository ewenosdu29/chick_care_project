from ultralytics import YOLO

dataset_yaml = "C:\\Users\\timch\\Documents\\AAACours\\nini\\chick_care_project\\ia\\Chick-Care_V2\\data.yaml"

model = YOLO('yolov8s.yaml')

model.train(data=dataset_yaml, epochs=100, imgsz=800, conf=0.5, lr0=0.01, lrf=0.1, momentum=0.937, weight_decay=0.0005, augment=True)

