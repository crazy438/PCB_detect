from ultralytics import YOLO # YOLO含Pytorch,Pytorch高版本神秘导包顺序bug，要让YOLO在QT前导入
from PyQt5.QtCore import QThread, pyqtSignal
from GUI.component import shared_data

class PredictTask(QThread):
    finished_signal = pyqtSignal()

    # parent需设置为父组件的self.parent()
    def __init__(self, parent=None):
        super().__init__(parent)
        # 业务顺序能够保证shared_data不会同时读写
        self.model = YOLO(shared_data.model_path)

    def run(self):
        results_list = [ self.model.predict(
            file_path,
            save=False,
            conf=shared_data.conf,
            iou=shared_data.IoU,
            imgsz=shared_data.imgsz,
        ) for file_path in shared_data.file_path_list]

        self.finished_signal.emit()