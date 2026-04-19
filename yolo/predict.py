from babel.localedata import exists
from ultralytics import YOLO
import cv2
if __name__ == '__main__':
    model = YOLO('../resource/models/PCB缺陷检测-YOLO26s.pt')
    # results = model.predict(
    #     source=0,
    #     save=False,
    #     stream=True,
    #     conf=0.25,
    #     iou=0.7,
    #     imgsz=1280,
    # )
    # for result in results:
    #     resized = cv2.resize(result.plot(), (1000, 800))
    #     cv2.imshow("Camera Detect (Press 'Q' to exit)", resized)
    #     if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(1) & 0xFF == ord('Q'):
    #         break
    model.predict(
        source=r"C:\Users\27843\Desktop\detection_platform\PCB_DATASET_YOLO\debug\01_missing_hole_04.jpg",
        verbose=False,
        save=False,
    )

    print(model.predictor)
    model.predict(
        source=r"C:\Users\27843\Desktop\detection_platform\PCB_DATASET_YOLO\debug\01_missing_hole_04.jpg",
        save_dir="output/nicm",
        save=True,
        verbose=False,
    )