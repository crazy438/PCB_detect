import pathlib
from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QImage, QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QHeaderView, QTableWidgetItem, QAbstractItemView
from qfluentwidgets import PushButton, HeaderCardWidget, FluentIcon, TableWidget, StateToolTip, MessageBox, \
    HorizontalFlipView

from .predict_task import predict_task
from shared_data import data


class ResultDisplayWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("检测结果")
        self.headerLabel.setObjectName("result_display_header")
        self.setBorderRadius(8)

        self.result_display_layout = QVBoxLayout()

        # 图像展示区域
        self.img_display_view = ImgDisplayView("图像预览区域", self)
        self.result_display_layout.addWidget(self.img_display_view, 3)

        self.init_buttons() # 初始化"开始检测"、"生成报告"按钮
        self.init_result_table() # 检测结果的表格
        self.init_thread() # 模型推理线程初始化

        # 要把组件和布局添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addLayout(self.result_display_layout)

        # 应用QSS
        qss_path = pathlib.Path(__file__).parent / "resource/result_display_widget.qss"
        with open( qss_path, encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def init_buttons(self):
        self.button_layout = QHBoxLayout()

        self.run_button = PushButton("🚀 开始处理")
        self.run_button.clicked.connect(self.model_predict)

        self.report_button = PushButton(FluentIcon.DOCUMENT, "生成报告")

        self.button_layout.addWidget(self.run_button)
        self.button_layout.addWidget(self.report_button)

        self.result_display_layout.addLayout(self.button_layout, 1)

    def init_result_table(self):
        self.result_table = TableWidget(self)
        self.result_table.setBorderVisible(True)
        self.result_table.setBorderRadius(8)
        self.result_table.setWordWrap(False)
        self.result_table.setSelectionBehavior(QAbstractItemView.SelectRows) # 单击选中整行
        self.result_table.setSelectionMode(QAbstractItemView.SingleSelection) # 一次只能选中一行，不允许选中多行
        self.result_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # 禁止编辑
        self.result_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                font-size: 20px;
                font-family: 'Microsoft YaHei';
                color: black;
            }
        """)
        self.result_table.verticalHeader().hide()
        self.result_table.setRowCount(5)
        self.result_table.setColumnCount(6)
        self.result_table.setHorizontalHeaderLabels(["缺陷类型", "置信度", "Xmin", "Xmax", "Ymin", "Ymax"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.result_display_layout.addWidget(self.result_table, 2)

        item = QTableWidgetItem("测试")
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        item.setFont(QFont("Microsoft YaHei", 14))
        self.result_table.setItem(0, 0, item)

    def model_predict(self):
        # 输入校验
        # conf, IoU, imgsz的输入校验已经在LineEdit()部分通过正则表达式完成
        if not data.model_path:
            w = CustomMessageBox("请加载模型", '左侧"模型设置"面板，点击"浏览"按钮加载模型', self.window())
            w.exec()
            return

        if not data.save_path:
            w = CustomMessageBox("请选择输出路径", '左侧"模型设置"面板，点击"浏览"按钮选择输出路径', self.window())
            w.exec()
            return

        if not (data.img_path_list or data.video_path_list):
            w = CustomMessageBox("请加载图片或视频文件", '左侧"推理设置"面板，点击"添加文件"按钮加载图片或视频', self.window())
            w.exec()
            return

        #  禁用按钮，防止处理期间再次触发
        self.run_button.setEnabled(False)
        self.report_button.setEnabled(False)

        # 弹出"正在处理"消息框
        self.process_message = ProcessMessage('正在处理中', '请耐心等待哦~~', self.parent())
        self.process_message.show()

        # 启动推理任务线程
        self.thread_manager.start()

    def init_thread(self):
        # 模型推理任务
        self.thread_manager = QThread() # 创建线程管理器
        predict_task.moveToThread(self.thread_manager)
        self.thread_manager.started.connect(predict_task.start)
        predict_task.finished_signal.connect(self.predict_finished_process)

    # 模型预测任务线程执行完后的后处理
    def predict_finished_process(self):
        self.thread_manager.quit() #  结束线程
        self.thread_manager.wait()  # 阻塞线程

        self.process_message.finished("处理完毕", f"结果已保存到{data.save_dir} 😆") # 结束"正在处理"消息框
        self.process_message = None
        self.run_button.setEnabled(True) # 恢复按钮
        self.report_button.setEnabled(True)

class ImgDisplayView(HorizontalFlipView):
    def __init__(self, tip_text=None, parent=None):
        super().__init__(parent)
        self.setAspectRatioMode(Qt.AspectRatioMode.IgnoreAspectRatio)
        self.setStyleSheet("border: 1px solid black;")
        self.tip_text = tip_text

    def add_image(self, img_path):
        self.clear()
        self.addImage(img_path)

        if data.save_dir:
            predict_img_path = data.save_dir / pathlib.Path(img_path).name
            if predict_img_path.exists():
                self.addImage(str(predict_img_path))

                # 延迟10ms切换索引, 给控件渲染时间
                QTimer.singleShot(10, lambda: self.setCurrentIndex(1))

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

# 隐藏掉cancel按钮的自定义样式QFluentWidget MessageBox
class CustomMessageBox(MessageBox):

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)
        # 内部有样式应用，外部QSS无法响应，只能追加样式写法
        self.titleLabel.setStyleSheet(self.titleLabel.styleSheet() + "#titleLabel {font-size: 25px;}")
        self.contentLabel.setStyleSheet(self.contentLabel.styleSheet() + "#contentLabel {font-size: 18px;}")

        self.yesButton.setFont(QFont("Microsoft YaHei", 16))
        self.cancelButton.hide()
        self.setContentCopyable(True)

# QFluentWidget的StateToolTip消息弹窗没有自动跟随特性，因此手写一个
class ProcessMessage(StateToolTip):
    def __init__(self, title, content, parent=None):
        super().__init__(title, content, parent)
        self.closeButton.hide() # 不需要关闭按钮
        self.titleLabel.setWordWrap(True) # 自动换行
        self.contentLabel.setWordWrap(True)
        self.update_position() # 更新位置

        self.window().window_resize_signal.connect(self.update_position)

    def update_position(self):
        self.move(self.parent().width() - self.width() - 10, 0)

    def finished(self, title, content):
        self.setTitle(title)
        self.setContent(content)
        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()
        self.setFixedSize(max(self.titleLabel.width(), self.contentLabel.width()) + 65, 75)
        self.titleLabel.move(32, 9)
        self.contentLabel.move(12, 27)

        # QFluentWidget有deleterLater流程，控件释放后QT会自动解绑与其相关的信号量，因此不用我们手动处理
        self.setState(True)