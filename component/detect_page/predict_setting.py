from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator, QFont, QStandardItem
from PyQt5.QtWidgets import QLabel, QFormLayout, QFileDialog
from qfluentwidgets import LineEdit, HeaderCardWidget, PushButton, FluentIcon

from custom_widget.file_list_widget import FileListView
from custom_widget.line_edit import CustomLineEdit
from custom_widget.model_choose_box import ModelChooseBox
from shared_data import shared_data
from utils.utils import is_img, is_video


class PredictSettingWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("推理设置")
        self.headerLabel.setObjectName("predict_setting_header")
        self.setBorderRadius(8)

        self.setting_layout = QFormLayout(self)

        self.model_choose_widget = ModelChooseBox(
            ("PCB缺陷检测-YOLO26s", "钢材表面缺陷检测-YOLO26s", "其他"),
            ("resource/models/PCB缺陷检测-YOLO26s.pt", "resource/models/钢材表面缺陷检测-YOLO26s.pt",  None)
        )
        self.model_choose_text = QLabel("模型选择")
        self.setting_layout.addRow(self.model_choose_text, self.model_choose_widget)

        self.save_widget = CustomLineEdit("输出路径")
        self.save_widget.button.clicked.connect(self.get_save_path)
        self.setting_layout.addRow(self.save_widget.text, self.save_widget.hbox)

        self.conf_text = QLabel("置信度阈值")
        self.conf_LineEdit = LineEdit()
        self.conf_LineEdit.setText("0.35")
        # ^0表示以0开头，\.为字符小数点，\d为0~9的数字，{0，4}表示重复\d 0~4次，|表示或
        self.conf_LineEdit.setValidator(QRegExpValidator(QRegExp(r"^0(\.\d{0,4})?$|^1(\.0{0,4})?$")))        # 正则表达式作输入验证
        self.conf_LineEdit.editingFinished.connect(self.update_conf)
        self.setting_layout.addRow(self.conf_text, self.conf_LineEdit)

        self.IoU_text = QLabel("IoU阈值")
        self.IoU_LineEdit = LineEdit()
        self.IoU_LineEdit.setText("0.7")
        self.IoU_LineEdit.setValidator(QRegExpValidator(QRegExp(r"^0(\.\d{0,4})?$|^1(\.0{0,4})?$")))
        self.IoU_LineEdit.editingFinished.connect(self.update_IoU)
        self.setting_layout.addRow(self.IoU_text, self.IoU_LineEdit)

        self.imgsz_text = QLabel("图像缩放大小")
        self.imgsz_LineEdit = LineEdit()
        self.imgsz_LineEdit.setText("1280")
        self.imgsz_LineEdit.setValidator(QRegExpValidator(QRegExp(r"^[1-9]\d{0,4}$")))
        self.imgsz_LineEdit.editingFinished.connect(self.update_imgsz)
        self.setting_layout.addRow(self.imgsz_text, self.imgsz_LineEdit)

        self.add_file_button = PushButton(FluentIcon.FOLDER, "添加文件")
        self.add_file_button.setObjectName("open_file_button")
        self.add_file_button.clicked.connect(lambda: self.get_file(QFont("Microsoft YaHei", 14)))
        self.setting_layout.addRow(self.add_file_button)

        # 加载文件的文件列表
        self.file_view = FileListView("文件选择区域")
        self.setting_layout.addRow(self.file_view)

        # 要把组件添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addLayout(self.setting_layout)

        # 应用QSS
        with open("resource/qss/predict_setting.qss", encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def get_save_path(self):
        save_path = QFileDialog.getExistingDirectory(self, "选择输出路径")
        if save_path:
            self.save_widget.line_edit.setText(save_path)
            shared_data.save_path = save_path

    def update_conf(self):
        shared_data.conf = eval(self.conf_LineEdit.text())

    def update_IoU(self):
        shared_data.IoU = eval(self.IoU_LineEdit.text())

    def update_imgsz(self):
        shared_data.imgsz = eval(self.imgsz_LineEdit.text())

    def get_file(self, qfont):
        file_path_list, _= QFileDialog.getOpenFileNames(self, "打开文件", filter="图片视频文件(*.jpg *.png *.bmp *.mp4 *.avi *.mkv)")
        if file_path_list:
            shared_data.process_imgs_timestamp = None
            self.file_view.clear_data()

            self.file_view.data_model.beginResetModel()
            for file in file_path_list:
                item = QStandardItem(file)
                item.setFont(qfont)
                self.file_view.data_model.appendRow(item)
            self.file_view.data_model.endResetModel()
            if self.file_view.currentIndex().row():
                self.file_view.setCurrentIndex(self.file_view.data_model.index(0, 0))
            else:
                self.file_view.flush_current_row()

            # 从文件路径列表file_path_list过滤出图片文件和视频文件
            img_path_list = []
            video_path_list = []
            for file_path in file_path_list:
                if is_img(file_path):
                    img_path_list.append(file_path)
                elif is_video(file_path):
                    video_path_list.append(file_path)
            shared_data.img_path_list = tuple(img_path_list)
            shared_data.video_path_list = tuple(video_path_list)