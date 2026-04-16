from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO('../resource/models/best.pt')
    model.predict(
        ["PCB_DATASET_YOLO/train/images/01_missing_hole_01.jpg", "PCB_DATASET_YOLO/train/images/01_missing_hole_02.jpg"],
        save_dir = "output/moderfuck",
        save=True,
        stream=True,
        conf=0.25,
        imgsz=1280,
    )

    model.predict(
        "PCB_DATASET_YOLO/debug/test_video.mp4",
        project="output",
        name="modetrfucl",
        save=True,
        verbose=True,
        conf=0.25,
        iou=0.7,
        imgsz=32,
    )