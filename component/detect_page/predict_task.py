import cv2
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable
from datetime import datetime
from pathlib import Path

from shared_data import shared_data, update_model_predicator, yolo_gc
from database import Database

class PredictSignals(QObject):
    finished_signal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)

# 业务顺序能够保证shared_data不会同时读写
class ImgPredictTask(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = PredictSignals()

    def run(self):
        # 只有参数发生变化才处理，阻止同样参数处理同样的图片视频
        if shared_data.is_changed:
            shared_data.save_dir = Path(shared_data.save_path) / datetime.now().strftime("%Y年%m月%d日%H时%M分%S秒%f毫秒")
            Path(shared_data.save_dir).mkdir(exist_ok=True) # 以当前时间创建输出文件夹

            # 采用视频流形式处理,返回帧生成器
            # YOLO内部神秘bug PR #23191: https://github.com/ultralytics/ultralytics/pull/23191
            # 清空yolo model的predictor,防止记忆上一次的设置
            # shared_data.model.predictor = None
            update_model_predicator()
            img_results = shared_data.model.predict(
                source=shared_data.img_path_list,
                save=False,
                stream=True,
                verbose=shared_data.verbose,
                conf=shared_data.conf,
                iou=shared_data.IoU,
                imgsz=shared_data.imgsz,
            )

            imgs_data = []
            defects_data = []
            shared_data.process_imgs_timestamp = []
            for i, img in enumerate(img_results):
                output_path = str(Path(shared_data.save_dir) / Path(shared_data.img_path_list[i]).name)
                img.save(filename=output_path)

                timestamp = int(datetime.now().timestamp() * 1000)
                shared_data.process_imgs_timestamp.append(timestamp)
                imgs_data.append((timestamp, output_path, shared_data.model_name))


                n_classes = len(img.boxes.cls)
                for j in range(n_classes):
                    cls = img.boxes.cls[j].item()
                    conf = img.boxes.conf[j].item()
                    xyxy = img.boxes.xyxy[j]
                    defects_data.append( ( timestamp, img.names[cls], round(conf,2), int(xyxy[0]), int(xyxy[2]), int(xyxy[1]), int(xyxy[3]) ) )

            # 将推理结果写入到数据库中
            with Database() as db:
                db.imgs_insert(imgs_data)
                db.defects_insert(defects_data)

            del img_results, imgs_data, defects_data

            # 清空yolo model的predictor,防止记忆上一次的设置
            update_model_predicator()
            for video in shared_data.video_path_list:
                shared_data.model.predict(
                    source=video,
                    save_dir=shared_data.save_dir,
                    save=True,
                    verbose=False,
                    conf=shared_data.conf,
                    iou=shared_data.IoU,
                    imgsz=shared_data.imgsz,
                )

            # 处理内存泄露
            yolo_gc()

            shared_data.is_changed = False  # 防止同样参数处理同样图片

        # 发送"完毕"信号
        self.signals.finished_signal.emit()

class CameraPredictTask(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = PredictSignals()
        self.is_running = True

    def run(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: 无法打开摄像头")
            self.signals.finished_signal.emit()
            return

        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                print("Warning: 无法获取帧")
                break
            # 清空yolo model的predictor,防止记忆上一次的设置
            update_model_predicator()

            results = shared_data.model.predict(
                source=frame,
                save=False,
                stream=True,
                verbose=False,
                conf=shared_data.conf,
                iou=shared_data.IoU,
                imgsz=shared_data.imgsz,
            )

            for result in results:
                img_resized = cv2.resize(result.plot(), (1000, 800))
                cv2.imshow("Camera Detect (Press 'Q' to exit)", img_resized)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                self.is_running = False
                break

        cap.release()
        cv2.destroyAllWindows()
        yolo_gc()
        self.signals.finished_signal.emit()
