import pathlib

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QHeaderView, QTableWidgetItem, QAbstractItemView
from qfluentwidgets import PushButton, HeaderCardWidget, FluentIcon, TableWidget

from .custom_widget.img_display_view import ImgDisplayView
from .custom_widget.message_box import CustomMessageBox
from .custom_widget.process_message import ProcessMessage
from .predict_task import PredictTask
from GUI.component import shared_data

class ResultDisplayWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("检测结果")
        self.headerLabel.setObjectName("result_display_header")
        self.setBorderRadius(8)

        self.result_display_layout = QVBoxLayout()

        ##########图像展示区域###########
        self.img_display_view = ImgDisplayView("图像预览区域", self)
        self.result_display_layout.addWidget(self.img_display_view, 3)

        self.init_buttons() # 初始化"开始检测"、"生成报告"按钮
        self.init_result_table() # 检测结果的表格

        # 模型推理任务
        self.thread_manager = QThread() # 创建线程管理器
        self.predict_task = PredictTask() # 创建模型推理任务的线程
        self.predict_task.moveToThread(self.thread_manager)
        self.thread_manager.started.connect(self.predict_task.start)
        self.predict_task.finished_signal.connect(self.predict_finished_process)

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

    def img_display(self, img_path):
        self.img_display_view.clear()
        self.img_display_view.addImage(img_path)

        if shared_data.time:
            save_dir = pathlib.Path(shared_data.save_path) / shared_data.time
            predict_img_path = save_dir / pathlib.Path(img_path).name
            if predict_img_path.exists():
                self.img_display_view.addImage(str(predict_img_path))
                self.img_display_view.setCurrentIndex(1)


    def model_predict(self):
        # 输入校验
        # conf, IoU, imgsz的输入校验已经在LineEdit()部分通过正则表达式完成
        if not shared_data.model_path:
            w = CustomMessageBox("请加载模型", '左侧"模型设置"面板，点击"浏览"按钮加载模型', self.window())
            w.exec()
            return

        if not shared_data.save_path:
            w = CustomMessageBox("请选择输出路径", '左侧"模型设置"面板，点击"浏览"按钮选择输出路径', self.window())
            w.exec()
            return

        if not (shared_data.img_path_list or shared_data.video_path_list):
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

    # 模型预测任务线程执行完后的后处理
    def predict_finished_process(self):
        self.thread_manager.quit() #  结束线程
        self.thread_manager.wait()  # 阻塞线程

        self.process_message.finished("处理完毕", f"结果已保存到{shared_data.save_path} 😆") # 结束"正在处理"消息框
        self.process_message = None
        self.run_button.setEnabled(True) # 恢复按钮
        self.report_button.setEnabled(True)
        self.img_display_view.setCurrentIndex(self.img_display_view.currentIndex())