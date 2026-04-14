from PyQt5.QtWidgets import QLabel, QHBoxLayout
from qfluentwidgets import PushButton, LineEdit, FluentIcon

class CustomLineEdit(LineEdit):
    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.text = QLabel(label_text)
        self.line_edit = LineEdit()
        self.line_edit.setReadOnly(True)
        self.button = PushButton(FluentIcon.FOLDER, "浏览")

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.line_edit)
        self.hbox.addWidget(self.button)