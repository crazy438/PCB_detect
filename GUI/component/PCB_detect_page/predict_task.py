from ultralytics import YOLO # YOLO含Pytorch,Pytorch高版本神秘导包顺序bug，要让YOLO在QT前导入
from PyQt5.QtCore import pyqtSignal, QObject
import torch
import gc
from datetime import datetime
from pathlib import Path

from GUI.component import shared_data


# YOLO自带的内存泄露问题，手动处理
def yolo_gc():
    torch.cuda.empty_cache() # 清理GPU缓存
    gc.collect()  # 触发Python GC

# 业务顺序能够保证shared_data不会同时读写
class PredictTask(QObject):
    # 模型推理完毕的信号
    started_signal = pyqtSignal()
    finished_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.model_path = ""
        self.model = None

    def start(self):
        self.started_signal.emit() # 通知PCB_detect_page禁用其他组件，防止数据竞争导致崩溃

        # 若模型路径shared_data.model_path没有发生变化,则不重复加载模型文件
        if self.model_path != shared_data.model_path:
            self.model_path = shared_data.model_path
            self.model = YOLO(shared_data.model_path)

        # 只有参数发生变化才处理，阻止同样参数处理同样的图片视频
        if shared_data.is_changed:
            shared_data.is_changed = False  # 防止同样参数处理同样图片
            shared_data.time = datetime.now().strftime("%Y年%m月%d日%H-%M-%S")
            save_dir = Path(shared_data.save_path) / shared_data.time
            Path(save_dir).mkdir(exist_ok=True) # 以当前时间创建输出文件夹

            img_results = self.model.predict(
                shared_data.img_path_list,
                save=True,
                save_dir=save_dir,
                verbose=shared_data.verbose,
                conf=shared_data.conf,
                iou=shared_data.IoU,
                imgsz=shared_data.imgsz,
            )

            # 获取输出图片, 重命名为原来的名字
            img_path_list = Path(save_dir).rglob("*")
            for img_path in img_path_list:
                if img_path.suffix in [".jpg", ".bmp", ".png"]:
                    id = eval(img_path.stem.split("image")[-1])
                    img_path.rename(img_path.with_name(Path(shared_data.img_path_list[id]).name))

            # 处理内存泄露
            yolo_gc()

            shared_data.predict_finished = True

        # 发送"完毕"信号
        self.finished_signal.emit()