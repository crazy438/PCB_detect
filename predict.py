from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO('best.pt')
    metrics = model.predict("PCB_DATASET_YOLO/train/images/01_missing_hole_01.jpg", device='0', save=False)
    print(metrics)