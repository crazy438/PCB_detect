import pathlib
import functools

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QColor
from PyQt5.QtWidgets import QHBoxLayout, QFileDialog, QButtonGroup, QListWidgetItem, QVBoxLayout
from qfluentwidgets import PushButton, HeaderCardWidget, FluentIcon, RadioButton, ListWidget
from PyQt5.QtCore import Qt

from GUI.component import shared_data


class PredictSettingWidget(HeaderCardWidget):
    # 将file_ListWidget选中的图片路径传递给result_display_widget.py里的img_display_region的信号量
    img_path_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("推理设置")
        self.headerLabel.setObjectName("predict_setting_header")
        self.setBorderRadius(8)

        # 推理设置布局
        self.predict_setting_layout = QVBoxLayout()

        # 初始化推理模式的三个互斥按钮
        self.init_predict_mode_button()

        # 初始化"添加文件"按钮
        self.add_file_button = PushButton(FluentIcon.FOLDER, "添加文件")
        self.add_file_button.setObjectName("open_file_button")
        self.add_file_button.clicked.connect(functools.partial(self.get_file, QFont("Microsoft YaHei", 14)))
        self.predict_setting_layout.addWidget(self.add_file_button)

        # 加载文件的文件列表
        self.file_ListWidget = FileListWidget("文件选择区域")
        self.file_ListWidget.itemSelectionChanged.connect(self.emit_img_path)
        self.predict_setting_layout.addWidget(self.file_ListWidget)

        # 要把组件和布局添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addLayout(self.predict_setting_layout)

        # 应用QSS
        qss_path = pathlib.Path(__file__).parent / "resource/predict_setting_widget.qss"
        with open( qss_path, encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def init_predict_mode_button(self):

        # QFluent内部用了setStyleSheet，导致QSS被阻断，只能外部附加样式写入
        self.img_video_mode_button = RadioButton("图片/视频模式", self)
        self.img_video_mode_button.setStyleSheet("font-size: 20px; font-family: 'Microsoft YaHei';")

        self.camera_mode_button = RadioButton("摄像头模式", self)
        self.camera_mode_button.setStyleSheet("font-size: 20px; font-family: 'Microsoft YaHei';")

        # 互斥按钮组
        self.predict_button_group = QButtonGroup(self)
        self.predict_button_group.addButton(self.img_video_mode_button)
        self.predict_button_group.addButton(self.camera_mode_button)

        # 选中第一个按钮
        self.img_video_mode_button.setChecked(True)

        # 水平分布
        self.predict_mode_layout = QHBoxLayout(self)
        self.predict_mode_layout.addWidget(self.img_video_mode_button)
        self.predict_mode_layout.addWidget(self.camera_mode_button)

        # 将"推理模式"Qlabel和按钮添加到布局里面
        self.predict_setting_layout.addLayout(self.predict_mode_layout)

    def get_file(self, qfont):
        file_path_list, _= QFileDialog.getOpenFileNames(self, "打开文件", filter="图片视频文件(*.jpg *.png *.bmp *.mp4 *.avi *.mkv)")
        if file_path_list:
            self.file_ListWidget.clear()
            for file in file_path_list:
                item = QListWidgetItem(file)
                item.setFont(qfont)
                self.file_ListWidget.addItem(item)
            self.file_ListWidget.setCurrentRow(0)
            shared_data.file_path_list = file_path_list

    def emit_img_path(self):
        selected_img_path = self.file_ListWidget.currentItem().text()

        # 若获取不到图片路径，直接返回
        if not selected_img_path: return

        # 将图片路径传递给result_display_widget.py里的img_display_region处理
        self.img_path_signal.emit(selected_img_path)

# 在QFluentWidget的ListWidget基础上，设定样式与实现空列表显示提示文字的功能
class FileListWidget(ListWidget):
    def __init__(self, tip_text=None, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setStyleSheet(self.styleSheet() + "ListWidget { border: 1px solid #A9A9A9; border-radius: 8px; }")
        self.tip_text = tip_text

    # 重写paintEvent事件，实现功能:列表为空时，显示"文件加载区域"这几个字，加载文件后不显示
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