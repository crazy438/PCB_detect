from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QLabel, QFormLayout, QFileDialog
from qfluentwidgets import LineEdit, HeaderCardWidget

from custom_widget.line_edit import CustomLineEdit
from shared_data import data


class QwenModelWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("质检报告")
        self.headerLabel.setObjectName("qwen_model_header")
        self.setBorderRadius(8)

        # 应用QSS
        with open("resource/qss/Qwen4b_model.qss", encoding='utf-8') as f:
            self.setStyleSheet(f.read())

