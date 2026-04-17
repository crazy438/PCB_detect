from PyQt5.QtCore import QThreadPool, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import PushButton, HeaderCardWidget

from custom_widget.img_display_view import ImgDisplayView
from custom_widget.message_box import CustomMessageBox
from custom_widget.process_message import ProcessMessage
from custom_widget.table_widget import CustomTableWidget
from .predict_task import ImgPredictTask, CameraPredictTask
from shared_data import data


class ResultDisplayWidget(HeaderCardWidget):
    predict_started_signal = pyqtSignal()
    predict_finished_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("检测结果")
        self.headerLabel.setObjectName("result_display_header")
        self.setBorderRadius(8)

        self.result_display_layout = QVBoxLayout()

        # 图像展示区域
        self.img_display_view = ImgDisplayView("图像预览区域", self)
        self.result_display_layout.addWidget(self.img_display_view, 3)

        # 初始化"开始检测"、"生成报告"按钮
        self.init_buttons()

        # 检测结果的表格
        self.result_table = CustomTableWidget(5, ["缺陷类型", "置信度", "Xmin", "Xmax", "Ymin", "Ymax"])
        self.result_display_layout.addWidget(self.result_table, 2)

        # 获取全局线程池
        self.pool = QThreadPool().globalInstance()

        # 要把组件和布局添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addLayout(self.result_display_layout)

        # 应用QSS
        with open("resource/qss/result_display_widget.qss", encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def init_buttons(self):
        self.run_button = PushButton("🚀 开始处理")
        self.run_button.clicked.connect(self.model_predict)
        self.headerLayout.addWidget(self.run_button)

        self.camera_button = PushButton("📷 摄像头检测")
        self.camera_button.clicked.connect(self.camera_predict)
        self.headerLayout.addWidget(self.camera_button)

    def model_predict(self):
        # 输入校验
        # conf, IoU, imgsz的输入校验已经在LineEdit()部分通过正则表达式完成
        if not data.model:
            w = CustomMessageBox("请加载模型", '左侧"推理设置"面板，点击"浏览"按钮加载模型', self.window())
            w.exec()
            return

        if not data.save_path:
            w = CustomMessageBox("请选择输出路径", '左侧"推理设置"面板，点击"浏览"按钮选择输出路径', self.window())
            w.exec()
            return

        if not (data.img_path_list or data.video_path_list):
            w = CustomMessageBox("请加载图片或视频文件", '左侧"推理设置"面板，点击"添加文件"按钮加载图片或视频', self.window())
            w.exec()
            return

        # 禁用整个检测页的交互,防止数据竞争
        self.predict_started_signal.emit()

        # 弹出"正在处理"消息框
        self.process_message = ProcessMessage('正在处理中', '请耐心等待哦~~', self)
        self.process_message.show()

        img_predict_task = ImgPredictTask()
        img_predict_task.signals.finished_signal.connect(self.predict_finished_process)
        self.pool.start(img_predict_task)

    def predict_finished_process(self):
        self.process_message.finished("处理完毕", f"结果已保存到{data.save_dir} 😆")  # 结束"正在处理"消息框
        self.process_message = None
        self.predict_finished_signal.emit()

    def camera_predict(self):
        if not data.model:
            w = CustomMessageBox("请加载模型", '左侧"推理设置"面板，点击"浏览"按钮加载模型', self.window())
            w.exec()
            return

        # 禁用整个检测页的交互,防止数据竞争
        self.predict_started_signal.emit()
        self.camera_button.setText("请按Q退出摄像头检测")

        camera_predict_task = CameraPredictTask()
        camera_predict_task.signals.finished_signal.connect(self.camera_predict_finished)
        self.pool.start(camera_predict_task)

    def camera_predict_finished(self):
        self.camera_button.setText("📷 摄像头检测")
        self.predict_finished_signal.emit()

    def add_results(self, current_row, img_path):
        if data.result_table_items:
            self.result_table.clearContents()
            labels, confs, coordinates = data.result_table_items[current_row]
            for i, label in enumerate(labels):
                self.result_table.add_item(i, 0, label)
            for i, conf in enumerate(confs):
                self.result_table.add_item(i, 1, conf)
            for i, (Xmin, Xmax, Ymin, Ymax) in enumerate(coordinates):
                self.result_table.add_item(i, 2, Xmin)
                self.result_table.add_item(i, 3, Xmax)
                self.result_table.add_item(i, 4, Ymin)
                self.result_table.add_item(i, 5, Ymax)