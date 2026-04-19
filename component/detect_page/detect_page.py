from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from .predict_setting import PredictSettingWidget
from .result_display import ResultDisplayWidget
from .ollama_model import OllamaModelWidget

class DetectPage(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        # QFluent要求必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))

        self.h_box_layout = QHBoxLayout(self)
        self.v_box_layout = QVBoxLayout(self)

        self.predict_setting_widget = PredictSettingWidget(self)
        self.result_display_widget = ResultDisplayWidget(self)
        self.ollama_model_widget = OllamaModelWidget(self)

        self.h_box_layout.addWidget(self.predict_setting_widget, 1)
        self.h_box_layout.addWidget(self.result_display_widget, 2)
        self.h_box_layout.addWidget(self.ollama_model_widget, 1)

        # 各个组件之间的信号通信
        self.signal_manage()

    def signal_manage(self):
        self.predict_setting_widget.file_view.current_row_signal.connect(self.result_display_widget.img_display_view.add_image)
        self.predict_setting_widget.file_view.current_row_signal.connect(self.result_display_widget.add_results)
        self.ollama_model_widget.report_button.clicked.connect(self.predict_setting_widget.file_view.emit_current_text)
        self.predict_setting_widget.file_view.current_text_signal.connect(lambda file_path: self.ollama_model_widget.run_ollama_model(file_path))

        # result_display里面的模型推理任务处理，禁用组件交互功能防止数据竞争导致崩溃
        self.result_display_widget.predict_started_signal.connect(lambda: self.setDisabled(True))
        self.result_display_widget.predict_finished_signal.connect(self.predict_setting_widget.file_view.flush_current_row)
        self.result_display_widget.predict_finished_signal.connect(lambda: self.setDisabled(False))