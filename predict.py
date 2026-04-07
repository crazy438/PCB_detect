from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO('best.pt')
    # metrics = model.predict(
    #     ["PCB_DATASET_YOLO/train/images/01_missing_hole_01.jpg", "PCB_DATASET_YOLO/train/images/01_missing_hole_02.jpg"],
    #     save=True,
    #     conf=0.25,
    #     imgsz=1280,
    # )
    metrics = model.predict(
        "GUI/media_player/video.mp4",
        save=True,
        conf=0.25,
        imgsz=1280,
    )
    print(metrics)