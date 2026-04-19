import gc

import torch
from PyQt5.QtCore import QObject

# YOLO自带的内存泄露问题，手动处理
def yolo_gc():
    torch.cuda.empty_cache() # 清理GPU缓存
    gc.collect()  # 触发Python GC
    gc.garbage.clear() # 触发循环垃圾回收


def update_model_predicator():
    shared_data.model.overrides['conf'] = shared_data.conf
    shared_data.model.overrides['iou'] = shared_data.IoU
    shared_data.model.overrides['imgsz'] = shared_data.imgsz
    shared_data.model.overrides['save_dir'] = shared_data.save_dir

class SharedData(QObject):
    # 内部数据存储（私有）
    def __init__(self):
        super().__init__()
        self.model = None
        self.model_name = None
        self.save_path: str = None
        self.save_dir: str = None
        self.conf = 0.25
        self.IoU = 0.7
        self.imgsz = 640
        self.img_path_list = None
        self.video_path_list = None
        self.is_changed = False
        self.is_new_file = False
        self.verbose = False # YOLO model.predict的调试信息是否输出
        self.process_imgs_timestamp = None
        self.database_path = "resource/history.db"
        self._attrs = (
            "model_name", "save_path", "conf", "IoU", "imgsz",
            "verbose", "img_path_list", "video_path_list",
        )

    def __setattr__(self, name, value):
        #  监听self._attrs内的变量变化,若有变化则设置self.is_changed=True
        if hasattr(self, name) and not self.is_changed and name in self._attrs and getattr(self, name) != value:
            self.is_changed = True

        # 调用原本的__setattr__
        super().__setattr__(name, value)

shared_data = SharedData()