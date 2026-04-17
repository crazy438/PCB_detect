from ultralytics import YOLO
import cv2
if __name__ == '__main__':
    model = YOLO('../resource/models/best.pt')
    results = model.predict(
        source=0,
        save=False,
        stream=True,
    )
    for result in results:
        cv2.imshow("yolo", result.plot())
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # model.predict(
    #     source=0,
    #     # save_dir = "output/moderfuck",
    #     save=False,
    #     show=True,
    #     # conf=0.25,
    #     # imgsz=1280,
    # )