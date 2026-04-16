from PyQt5.QtCore import QObject

class SharedData(QObject):
    # 内部数据存储（私有）
    def __init__(self):
        super().__init__()
        self.model_path: str = None
        self.save_path: str = None
        self.save_dir: str = None
        self.conf = 0.25
        self.IoU = 0.7
        self.imgsz = 640
        self.img_path_list = None
        self.video_path_list = None
        self.is_changed = False
        self.verbose = False # YOLO model.predict的调试信息是否输出
        self.result_table_items = None
        self._attrs = (
            "model_path", "save_path", "conf", "IoU", "imgsz",
            "verbose", "img_path_list", "video_path_list",
        )

    def __setattr__(self, name, value):
        #  监听self._attrs内的变量变化,若有变化则设置self.is_changed=True
        if hasattr(self, name) and not self.is_changed and name in self._attrs and getattr(self, name) != value:
            self.is_changed = True

        # 调用原本的__setattr__
        super().__setattr__(name, value)

data = SharedData()