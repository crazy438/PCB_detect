from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from .model_setting import ModelSettingWidget
from .predict_setting import PredictSettingWidget
from .result_display import ResultDisplayWidget


class PCBDetectPage(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        # QFluent要求必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))

        self.h_box_layout = QHBoxLayout(self)
        self.v_box_layout_1 = QVBoxLayout(self)
        self.v_box_layout_2 = QVBoxLayout(self)

        self.model_setting_widget = ModelSettingWidget(self)
        self.predict_setting_widget = PredictSettingWidget(self)
        self.result_display_widget = ResultDisplayWidget(self)

        self.predict_setting_widget.img_path_signal.connect(self.result_display_widget.img_display)

        ####################layout设置#####################
        self.h_box_layout.addLayout(self.v_box_layout_1, 2)
        self.h_box_layout.addLayout(self.v_box_layout_2, 3)
        self.v_box_layout_1.addWidget(self.model_setting_widget)
        self.v_box_layout_1.addWidget(self.predict_setting_widget)
        self.v_box_layout_2.addWidget(self.result_display_widget)
