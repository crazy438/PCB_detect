from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QFileDialog
from qfluentwidgets import EditableComboBox, setFont
from ultralytics import YOLO

from shared_data import data


class ModelChooseBox(EditableComboBox):
    def __init__(self, choices, model_path, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("请选择一个模型")
        self.model_path = model_path
        self.addItems(choices)
        self.setCurrentIndex(-1)
        self.previous_index = -1
        self.last_index = len(choices) - 1
        self.currentIndexChanged.connect(self.get_model_path)
        self.setMaximumWidth(350)

        setFont(self, 20)

    def get_model_path(self, index):
        if index == self.last_index:
            model_path, _ = QFileDialog.getOpenFileName(self, "打开模型文件", filter="模型文件(*.pt)")
            if model_path:
                self.setText(model_path)
                data.model_path = model_path
            else:
                self.setCurrentIndex(self.previous_index)
        else:
            self.previous_index = index
            data.model_path = self.model_path[index]