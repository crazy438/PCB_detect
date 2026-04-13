from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO('best.pt')
    metrics = model.predict(
        ["PCB_DATASET_YOLO/train/images/01_missing_hole_01.jpg", "PCB_DATASET_YOLO/train/images/01_missing_hole_02.jpg"],
        save=False,
        stream=True,
        conf=0.25,
        imgsz=1280,
    )
    for i in metrics:
        print(i)

    # metrics = model.predict(
    #     ["PCB_DATASET_YOLO/debug/01_missing_hole_04.jpg", "PCB_DATASET_YOLO/debug/01_spur_10.jpg"],
    #     save_dir="fuck_test",
    #     save=True,
    #     save_txt=True,
    #     conf=0.25,
    #     imgsz=1280,
    # )
    # metrics = model.predict(
    #     ["PCB_DATASET_YOLO/debug/07_spurious_copper_03.jpg", "PCB_DATASET_YOLO/debug/12_missing_hole_10.jpg"],
    #     save_dir="fuck_test",
    #     save=True,
    #     conf=0.25,
    #     imgsz=32,
    # )
    print(metrics)