import cv2
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable
import torch
import gc
from datetime import datetime
from pathlib import Path
from shared_data import data

# YOLO自带的内存泄露问题，手动处理
def yolo_gc():
    torch.cuda.empty_cache() # 清理GPU缓存
    gc.collect()  # 触发Python GC
    gc.garbage.clear() # 触发循环垃圾回收

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
        if data.is_changed:
            data.save_dir = Path(data.save_path) / datetime.now().strftime("%Y年%m月%d日%H-%M-%S")
            Path(data.save_dir).mkdir(exist_ok=True) # 以当前时间创建输出文件夹

            # 采用视频流形式处理,返回帧生成器
            # YOLO内部神秘bug PR #23191: https://github.com/ultralytics/ultralytics/pull/23191
            # 清空yolo model的predictor,防止记忆上一次的设置
            data.model.predictor = None

            img_results = data.model.predict(
                source=data.img_path_list,
                save=False,
                stream=True,
                verbose=data.verbose,
                conf=data.conf,
                iou=data.IoU,
                imgsz=data.imgsz,
            )

            data.result_table_items = []

            for i, img in enumerate(img_results):
                output_name = Path(data.img_path_list[i]).name
                img.save(filename=Path(data.save_dir) / output_name)

                # img.names是类别id->类别的字典, img.boxes.cls是每个框的类别id
                labels = [ img.names[cls.item()] for cls in img.boxes.cls ]

                confs = [ round(conf.item(),2) for conf in img.boxes.conf ]

                # 将每个框的xyxy格式转为(Xmin, Xmax, Ymin, Ymax)格式
                xxyy = [ (int(xyxy[0].item()), int(xyxy[2].item()), int(xyxy[1].item()), int(xyxy[3].item())) for xyxy in img.boxes.xyxy ]

                data.result_table_items.append((labels, confs, xxyy))

            del img_results

            # 清空yolo model的predictor,防止记忆上一次的设置
            data.model.predictor = None

            for video in data.video_path_list:
                data.model.predict(
                    source=video,
                    save_dir=data.save_dir,
                    save=True,
                    verbose=False,
                    conf=data.conf,
                    iou=data.IoU,
                    imgsz=data.imgsz,
                )

            # 处理内存泄露
            yolo_gc()

            data.is_changed = False  # 防止同样参数处理同样图片

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
            data.model.predictor = None

            results = data.model.predict(
                source=frame,
                save=False,
                stream=True,
                verbose=False,
                conf=data.conf,
                iou=data.IoU,
                imgsz=data.imgsz,
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