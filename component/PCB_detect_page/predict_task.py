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
        self.model_path = ""
        self.model = None

    def start(self):
        self.started_signal.emit() # 通知PCB_detect_page禁用其他组件，防止数据竞争导致崩溃

        # data.model_path发生了变化才加载新的模型
        if self.model_path != data.model_path:
            self.model_path = data.model_path
            self.model = YOLO(self.model_path)

        # 只有参数发生变化才处理，阻止同样参数处理同样的图片视频
        if data.is_changed:
            data.save_dir = Path(data.save_path) / datetime.now().strftime("%Y年%m月%d日%H-%M-%S")
            Path(data.save_dir).mkdir(exist_ok=True) # 以当前时间创建输出文件夹

            # 采用视频流形式处理,返回帧生成器
            img_results = self.model.predict(
                data.img_path_list,
                save=False,
                stream=True,
                verbose=data.verbose,
                conf=data.conf,
                iou=data.IoU,
                imgsz=data.imgsz,
            )

            for i, img in enumerate(img_results):
                output_name = Path(data.img_path_list[i]).name
                img.save(filename=Path(data.save_dir) / output_name)

            del img_results

            # 处理内存泄露
            yolo_gc()

            data.is_changed = False  # 防止同样参数处理同样图片
        # 发送"完毕"信号
        self.finished_signal.emit()

predict_task = PredictTask()