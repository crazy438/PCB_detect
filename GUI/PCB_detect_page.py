import pathlib
from PyQt5.QtCore import Qt, QStandardPaths
from PyQt5.Qt import QPixmap, QPainter, QPoint, QPen, QColor, QSize, QBrush
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QFormLayout, QWidget, QFileDialog

from .model_setting_widget import ModelSettingWidget
from .predict_setting_widget import PredictSettingWidget
from .result_display_widget import ResultDisplayWidget


class PCBDetectPage(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        # QFluent要求必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))

        self.h_box_layout = QHBoxLayout(self)
        self.v_box_layout_1 = QVBoxLayout()
        self.v_box_layout_2 = QVBoxLayout()

        self.model_setting_widget = ModelSettingWidget(self)
        self.predict_setting_widget = PredictSettingWidget(self)
        self.result_display_widget = ResultDisplayWidget(self)

        ####################layout设置#####################
        self.h_box_layout.addLayout(self.v_box_layout_1, 2)
        self.h_box_layout.addLayout(self.v_box_layout_2, 3)
        self.v_box_layout_1.addWidget(self.model_setting_widget)
        self.v_box_layout_1.addWidget(self.predict_setting_widget)
        self.v_box_layout_2.addWidget(self.result_display_widget)
