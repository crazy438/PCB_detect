from ultralytics import YOLO
from PyQt5.QtCore import QRunnable, QThreadPool
from PyQt5.QtWidgets import QFileDialog
from qfluentwidgets import EditableComboBox, setFont

from shared_data import data

class ModelChooseBox(EditableComboBox):
    def __init__(self, choices, model_path_list, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("请选择一个模型")
        self.model_path_list = model_path_list
        self.addItems(choices)
        self.setCurrentIndex(-1)
        self.previous_index = -1
        self.last_index = len(choices) - 1
        self.currentIndexChanged.connect(self.get_model_path)
        self.setMaximumWidth(350)
        setFont(self, 20)
        self.pool = QThreadPool().globalInstance() # 获取全局线程池

    def get_model_path(self, index):
        if index == self.last_index:
            selected_model_path, _ = QFileDialog.getOpenFileName(self, "打开模型文件", filter="模型文件(*.pt)")
            if selected_model_path:
                self.setText(selected_model_path)
                model_path = selected_model_path
            else:
                self.setCurrentIndex(self.previous_index)
                return
        else:
            self.previous_index = index
            model_path = self.model_path_list[index]

        # 线程池创建线程加载模型
        load_model_task = LoadModelTask(model_path)
        self.pool.start(load_model_task)

class LoadModelTask(QRunnable):
    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path

    def run(self):
        data.model = YOLO(self.model_path)