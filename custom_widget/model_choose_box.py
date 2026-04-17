from ultralytics import YOLO
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QWaitCondition, QMutex
from PyQt5.QtWidgets import QFileDialog
from qfluentwidgets import EditableComboBox, setFont


from shared_data import data


class ModelChooseBox(EditableComboBox):
    trigger_signal = pyqtSignal(str)
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

        # 持久化线程加载模型
        self.thread = QThread()
        self.load_model_task = LoadModelTask()
        self.trigger_signal.connect(self.load_model_task.start)
        self.load_model_task.moveToThread(self.thread)
        self.thread.started.connect(self.load_model_task.run)
        self.thread.start()

    def get_model_path(self, index):
        if index == self.last_index:
            model_path, _ = QFileDialog.getOpenFileName(self, "打开模型文件", filter="模型文件(*.pt)")
            if model_path:
                self.setText(model_path)
                self.trigger_signal.emit(model_path)
            else:
                self.setCurrentIndex(self.previous_index)
        else:
            self.previous_index = index
            self.trigger_signal.emit(self.model_path_list[index])

class LoadModelTask(QObject):
    def __init__(self):
        super().__init__()
        self.is_pause = True
        self.model_path = None
        self.cond = QWaitCondition()
        self.mutex = QMutex()

    def start(self, model_path):
        self.is_pause = False
        self.model_path = model_path
        self.cond.wakeAll()

    def run(self):
        while 1:
            self.mutex.lock()
            if self.is_pause:
                self.cond.wait(self.mutex) # 暂停时就挂起线程

            data.model = YOLO(self.model_path)
            self.is_pause=True
            self.mutex.unlock()