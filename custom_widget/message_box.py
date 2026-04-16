# 隐藏掉cancel按钮的自定义样式QFluentWidget MessageBox
from PyQt5.QtGui import QFont
from qfluentwidgets import MessageBox, setFont


class CustomMessageBox(MessageBox):

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)
        # 内部有样式应用，外部QSS无法响应，只能追加样式写法
        self.titleLabel.setStyleSheet(self.titleLabel.styleSheet() + "#titleLabel {font-size: 25px;}")
        self.contentLabel.setStyleSheet(self.contentLabel.styleSheet() + "#contentLabel {font-size: 18px;}")

        self.yesButton.setFont(QFont("Microsoft YaHei", 16))
        self.cancelButton.hide()
        self.setContentCopyable(True)