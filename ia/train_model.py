from ultralytics import YOLO

dataset_yaml = "C:\\Users\\timch\\Documents\\AAACours\\nini\\Chick-Care_V2.v2i.yolov8\\data.yaml"

model = YOLO('yolov8n.yaml')

model.train(data=dataset_yaml, epochs=50, imgsz=640)
