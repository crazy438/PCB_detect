# coding:utf-8
from ultralytics import YOLO # YOLO含有Pytorch,高版本Pytorch的神秘bug要求在QT前导入
import asyncio
import threading
import qasync
import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QHBoxLayout, QApplication

from qfluentwidgets import NavigationBar, NavigationItemPosition, MessageBox
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow

from component.detect_page.detect_page import DetectPage
from component.history_page.history_page import HistoryPage
from custom_widget.main_window_widget import CustomTitleBar, StackedWidget
from utils import start_ollama_server

class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationBar = NavigationBar(self)
        self.stackWidget = StackedWidget(self)

        # create sub interface
        self.detect_page = DetectPage("PCB检测页面", self)
        self.history_page = HistoryPage("历史记录", self)
        self.detect_page.result_display_widget.predict_finished_signal.connect(
            self.history_page.history_table_widget.history_table.flush_history_table
        )

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.detect_page, FIF.HOME, "缺陷检测", selectedIcon=FIF.HOME_FILL)
        self.addSubInterface(self.history_page, FIF.HISTORY, "历史记录")
        self.navigationBar.addItem(
            routeKey='Help',
            icon=FIF.HELP,
            text='帮助',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.detect_page.objectName())

    def initWindow(self):
        self.resize(1500, 800)
        self.setWindowIcon(QIcon("resource/广大校徽.png"))
        self.setWindowTitle("基于PyQt5的缺陷检测平台")
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        # 应用QSS
        with open("resource/qss/main.qss", encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def addSubInterface(self, interface, icon, text: str, position=NavigationItemPosition.TOP, selectedIcon=None):
        """ add sub interface """
        self.stackWidget.addWidget(interface)
        self.navigationBar.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switchTo(interface),
            selectedIcon=selectedIcon,
            position=position,
        )

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        w = MessageBox(
            '支持作者🥰',
            '您的支持就是作者开发和维护项目的动力🚀',
            self
        )
        w.yesButton.setText('来啦老弟')
        w.cancelButton.setText('下次一定')

        if w.exec():
            QDesktopServices.openUrl(QUrl("https://github.com/crazy438/PCB_detect"))

if __name__ == '__main__':
    # 程序启动时: 自动检查并开启ollama server用于调用本地大模型api
    threading.Thread(target=start_ollama_server, daemon=True).start()

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)

    # qasync
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    w = Window()
    w.show()

    with loop:
        loop.run_forever()