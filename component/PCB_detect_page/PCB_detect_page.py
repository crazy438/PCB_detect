from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from .model_setting import ModelSettingWidget
from .predict_setting import PredictSettingWidget
from .result_display import ResultDisplayWidget
from .predict_task import predict_task

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

        ####################layout设置#####################
        self.h_box_layout.addLayout(self.v_box_layout_1, 2)
        self.h_box_layout.addLayout(self.v_box_layout_2, 3)
        self.v_box_layout_1.addWidget(self.model_setting_widget)
        self.v_box_layout_1.addWidget(self.predict_setting_widget)
        self.v_box_layout_2.addWidget(self.result_display_widget)

        # 各个组件之间的信号通信
        self.signal_manage()

    def signal_manage(self):
        self.predict_setting_widget.file_ListWidget.current_row_signal.connect(self.result_display_widget.img_display_view.add_image)
        self.predict_setting_widget.file_ListWidget.current_row_signal.connect(self.result_display_widget.result_table.add_item_from_results)

        # result_display里面的模型推理任务处理，禁用其他组件防止数据竞争导致崩溃
        predict_task.started_signal.connect(self.disable_widget)
        predict_task.finished_signal.connect(self.predict_setting_widget.file_ListWidget.flush_current_row)
        predict_task.finished_signal.connect(self.enable_widget)

    def disable_widget(self):
        self.model_setting_widget.setDisabled(True)
        self.predict_setting_widget.setDisabled(True)

    def enable_widget(self):
        self.model_setting_widget.setDisabled(False)
        self.predict_setting_widget.setDisabled(False)