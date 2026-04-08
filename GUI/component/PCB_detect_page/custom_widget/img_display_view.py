from PyQt5.QtGui import QPainter, QColor, QFont
from qfluentwidgets import HorizontalFlipView
from PyQt5.QtCore import Qt

class ImgDisplayView(HorizontalFlipView):
    def __init__(self, tip_text=None, parent=None):
        super().__init__(parent)
        self.setAspectRatioMode(Qt.AspectRatioMode.IgnoreAspectRatio)
        self.setStyleSheet("border: 1px solid black;")
        self.tip_text = tip_text

    # 重写paintEvent事件，实现功能:列表为空时，显示"图像预览区域"这几个字，加载图像后不显示
    def paintEvent(self, event):
        # 先调用父类的 paintEvent，保证正常绘制列表项和边框
        super().paintEvent(event)

        if self.count() == 0 and self.tip_text:
            # 在视口上绘制，避开列表区域
            painter = QPainter(self.viewport())

            # 设置文本样式
            painter.setPen(QColor(150, 150, 150))
            painter.setFont(QFont("Microsoft YaHei", 25))

            # 获取视口矩形，在中间绘制文本
            viewport_rect = self.viewport().rect()
            painter.drawText(viewport_rect, Qt.AlignCenter, self.tip_text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setItemSize(self.size()) # 神人作者没写resizeEvent的ItemSize更新