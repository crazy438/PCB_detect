import pathlib

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QFormLayout, QWidget, QFileDialog, QButtonGroup, QListWidgetItem, \
    QListWidget, QVBoxLayout
from qfluentwidgets import PushButton, LineEdit, HeaderCardWidget, FluentIcon, RadioButton, ListWidget

class ResultDisplayWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("检测结果")
        self.headerLabel.setObjectName("result_display_header")
        self.setBorderRadius(8)

        self.result_display_layout = QVBoxLayout()

        ##########图像展示区域###########
        self.img_display_region = QLabel()
        self.img_display_region.setObjectName("result_display_region")
        self.img_display_region.setText("图像展示区域")
        self.img_display_region.setAlignment(Qt.AlignCenter)
        self.img_display_region.setStyleSheet("border: 1px solid black;")
        self.img_display_region.setScaledContents(True)
        self.result_display_layout.addWidget(self.img_display_region)

        # 初始化"开始检测"、"生成报告"、"保存图像"按钮
        self.init_buttons()

        # 要把组件和布局添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addLayout(self.result_display_layout)

        # 应用QSS
        qss_path = pathlib.Path(__file__).parent / "resource/result_display_widget.qss"
        with open( qss_path, encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def init_buttons(self):
        self.button_layout = QHBoxLayout()

        self.run_button = PushButton("🚀 开始检测")
        self.report_button = PushButton(FluentIcon.DOCUMENT, "生成报告")
        self.save_button = PushButton(FluentIcon.SAVE, "保存图像")

        self.button_layout.addWidget(self.run_button)
        self.button_layout.addWidget(self.report_button)
        self.button_layout.addWidget(self.save_button)

        self.result_display_layout.addLayout(self.button_layout)