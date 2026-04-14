# 在QFluentWidget的ListWidget基础上，实现设定样式,空列表显示提示文字,选中行切换信号的功能
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QColor, QStandardItemModel
from networkx.classes import is_empty
from qfluentwidgets import ListView


class FileListView(ListView):
    # 将选中的图片路径传递给result_display_widget.py里的img_display_view
    current_row_signal = pyqtSignal(int, str)

    def __init__(self, tip_text=None, parent=None):
        super().__init__(parent)
        self.tip_text = tip_text

        self.setAlternatingRowColors(True)
        self.setStyleSheet(self.styleSheet() + "ListView { border: 1px solid #A9A9A9; border-radius: 8px; }")

        self.data_model = QStandardItemModel()
        self.setModel(self.data_model)
        self.selectionModel().currentRowChanged.connect(self.emit_current_item)

    def is_empty(self):
        return self.data_model and self.data_model.rowCount() == 0

    def clear_data(self):
        if not self.is_empty():
            self.data_model.removeRows(0, self.data_model.rowCount())

    def emit_current_item(self, current, previous):
        selected_img_path = current.data()

        # 将图片路径传递给result_display_widget.py里的img_display_view处理
        if selected_img_path:
            self.current_row_signal.emit(current.row(), selected_img_path)

    def flush_current_row(self):
        self.clicked.emit(self.currentIndex())

    # 重写paintEvent事件，实现功能:列表为空时，显示"文件加载区域"这几个字，加载文件后不显示
    def paintEvent(self, event):
        # 先调用父类的 paintEvent，保证正常绘制列表项和边框
        super().paintEvent(event)

        if self.is_empty() and self.tip_text:
            # 在视口上绘制，避开列表区域
            painter = QPainter(self.viewport())

            # 设置文本样式
            painter.setPen(QColor(150, 150, 150))
            painter.setFont(QFont("Microsoft YaHei", 25))

            # 获取视口矩形，在中间绘制文本
            viewport_rect = self.viewport().rect()
            painter.drawText(viewport_rect, Qt.AlignCenter, self.tip_text)