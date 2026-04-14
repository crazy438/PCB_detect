import pathlib
import functools

from PyQt5.QtGui import QFont, QStandardItem
from PyQt5.QtWidgets import QHBoxLayout, QFileDialog, QButtonGroup, QListWidgetItem, QVBoxLayout
from qfluentwidgets import PushButton, HeaderCardWidget, FluentIcon, RadioButton, ListWidget

from custom_widget.file_list_widget import FileListView
from shared_data import data


class PredictSettingWidget(HeaderCardWidget):
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
        self.file_view = FileListView("文件选择区域")
        self.predict_setting_layout.addWidget(self.file_view)

        # 要把组件和布局添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addLayout(self.predict_setting_layout)

        # 应用QSS
        with open( "resource/predict_setting_widget.qss", encoding='utf-8') as f:
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
            self.file_view.clear_data()

            self.file_view.data_model.beginResetModel()
            for file in file_path_list:
                item = QStandardItem(file)
                item.setFont(qfont)
                self.file_view.data_model.appendRow(item)
            self.file_view.data_model.endResetModel()
            self.file_view.setCurrentIndex(self.file_view.data_model.index(0,0))

            # 从文件路径列表file_path_list过滤出图片文件和视频文件
            img_path_list = []
            video_path_list = []
            for file_path in file_path_list:
                if pathlib.Path(file_path).suffix in [".jpg", ".png", ".bmp"]:
                    img_path_list.append(file_path)
                elif pathlib.Path(file_path).suffix in [".mp4", ".avi", ".mkv"]:
                    video_path_list.append(file_path)
            data.img_path_list = img_path_list
            data.video_path_list = video_path_list