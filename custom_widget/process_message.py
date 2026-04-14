# QFluentWidget的StateToolTip消息弹窗没有自动跟随特性，因此手写一个
from qfluentwidgets import StateToolTip

class ProcessMessage(StateToolTip):
    def __init__(self, title, content, parent=None):
        super().__init__(title, content, parent)
        self.closeButton.hide() # 不需要关闭按钮
        self.titleLabel.setWordWrap(True) # 自动换行
        self.contentLabel.setWordWrap(True)
        self.setFixedSize(max(self.titleLabel.width(), self.contentLabel.width()) + 56,
                            self.titleLabel.height() + self.contentLabel.height() + 15)
        self.update_position() # 更新位置
        self.window().window_resize_signal.connect(self.update_position)

    def update_position(self):
        self.move(self.parent().width() - self.width() - 10, 0)

    def finished(self, title, content):
        self.setTitle(title)
        self.setContent(content)
        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()
        self.setFixedSize(max(self.titleLabel.width(),self.contentLabel.width()) + 70, self.titleLabel.height() + self.contentLabel.height() + 15)
        self.titleLabel.move(32, 9)
        self.contentLabel.move(12, 27)

        # QFluentWidget有deleterLater流程，控件释放后QT会自动解绑与其相关的信号量，因此不用我们手动处理
        self.setState(True)