from ultralytics import YOLO # YOLO含Pytorch,Pytorch高版本神秘导包顺序bug，要让YOLO在QT前导入
from PyQt5.QtCore import pyqtSignal, QObject
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

# 业务顺序能够保证shared_data不会同时读写
class PredictTask(QObject):
    # 模型推理启动和完毕的信号
    started_signal = pyqtSignal()
    finished_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

    def start(self):
        self.started_signal.emit() # 通知PCB_detect_page禁用其他组件，防止数据竞争导致崩溃

        # 只有参数发生变化才处理，阻止同样参数处理同样的图片视频
        if data.is_changed:
            data.save_dir = Path(data.save_path) / datetime.now().strftime("%Y年%m月%d日%H-%M-%S")
            Path(data.save_dir).mkdir(exist_ok=True) # 以当前时间创建输出文件夹

            # 采用视频流形式处理,返回帧生成器
            # YOLO内部神秘bug PR #23191: https://github.com/ultralytics/ultralytics/pull/23191
            # 即使save=False也要设置save_dir, 后面再设置则无效
            img_results = data.model.predict(
                source=data.img_path_list,
                save_dir=data.save_dir,
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
        self.finished_signal.emit()

predict_task = PredictTask()