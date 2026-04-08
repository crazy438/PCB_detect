from qfluentwidgets import StateToolTip

# QFluentWidget的StateToolTip消息弹窗没有自动跟随特性，因此手写一个
class ProcessMessage(StateToolTip):
    def __init__(self, title, content, parent=None):
        super().__init__(title, content, parent)
        self.closeButton.hide()
        self.update_position()
        self.window().window_resize_signal.connect(self.update_position)

    def update_position(self):
        self.move(self.parent().width() - self.width() - 10, 0)

    def finished(self):
        self.setState(True)
        self.window().window_resize_signal.disconnect(self.update_position)
        self.deleteLater()