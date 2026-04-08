import pathlib

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QHeaderView, QTableWidgetItem, QAbstractItemView
from qfluentwidgets import PushButton, HeaderCardWidget, FluentIcon, TableWidget, \
    MessageBox

from GUI.component.PCB_detect_page.custom_widget.img_display_view import ImgDisplayView
from GUI.component import shared_data
from GUI.component.PCB_detect_page.custom_widget.process_message import ProcessMessage


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

        self.init_buttons() # 初始化"开始检测"、"生成报告"、"保存图像"按钮
        self.init_result_table() # 检测结果的表格

        # 要把组件和布局添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addLayout(self.result_display_layout)

        # 应用QSS
        qss_path = pathlib.Path(__file__).parent / "resource/result_display_widget.qss"
        with open( qss_path, encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def init_buttons(self):
        self.button_layout = QHBoxLayout()

        self.run_button = PushButton("🚀 开始检测")
        self.run_button.clicked.connect(self.model_predict)

        self.report_button = PushButton(FluentIcon.DOCUMENT, "生成报告")
        self.save_button = PushButton(FluentIcon.SAVE, "保存图像")

        self.button_layout.addWidget(self.run_button)
        self.button_layout.addWidget(self.report_button)
        self.button_layout.addWidget(self.save_button)

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

    def model_predict(self):
        # 输入校验
        # conf, IoU, imgsz的输入校验已经在LineEdit()部分通过正则表达式完成

        if not shared_data.model_path:
            w = MyMessageBox("请加载模型", '左侧"模型设置"面板，点击"浏览"按钮加载模型', self.window())
            w.exec()
            return

        if not shared_data.file_path_list:
            w = MyMessageBox("请加载图片", '左侧"推理设置"面板，点击"添加文件"按钮加载图片或视频', self.window())
            w.exec()
            return

        #  禁用"开始检测"按钮，防止处理期间再次触发
        self.run_button.setEnabled(False)

        # 弹出"正在处理"消息框
        self.process_message = ProcessMessage('正在处理中', '请耐心等待哦~~', self.parent())
        self.process_message.show()

    def predict_finished_process(self):
        self.process_message.finished() # 结束"正在处理"消息框
        self.run_button.setEnabled(True) # 恢复按钮

# 隐藏掉cancel按钮的自定义样式QFluentWidget MessageBox
class MyMessageBox(MessageBox):

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(title, content, parent)
        # 内部有样式应用，外部QSS无法响应，只能追加样式写法
        self.titleLabel.setStyleSheet(self.titleLabel.styleSheet() + "#titleLabel {font-size: 25px;}")
        self.contentLabel.setStyleSheet(self.contentLabel.styleSheet() + "#contentLabel {font-size: 18px;}")

        self.yesButton.setFont(QFont("Microsoft YaHei", 16))
        self.cancelButton.hide()
        self.setContentCopyable(True)