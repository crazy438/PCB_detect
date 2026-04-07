import pathlib

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QDoubleValidator, QValidator, QRegExpValidator, QIntValidator
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QFormLayout, QFileDialog
from qfluentwidgets import PushButton, LineEdit, HeaderCardWidget, FluentIcon

from . import shared_data

class ModelSettingWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("模型设置")
        self.headerLabel.setObjectName("model_setting_header")
        self.setBorderRadius(8)

        self.model_setting_layout = QFormLayout()

        self.model_path_text = QLabel("模型路径")
        self.model_path_LineEdit = LineEdit()
        self.model_path_LineEdit.setReadOnly(True)

        self.open_file_button = PushButton(FluentIcon.FOLDER, "浏览")
        self.open_file_button.setObjectName("open_file_button")
        self.open_file_button.clicked.connect(self.get_model_file)
        self.model_path_hbox = QHBoxLayout()
        self.model_path_hbox.addWidget(self.model_path_LineEdit)
        self.model_path_hbox.addWidget(self.open_file_button)

        self.model_conf_text = QLabel("置信度阈值")
        self.model_conf_LineEdit = LineEdit()
        self.model_conf_LineEdit.setText("0.25")
        self.model_conf_LineEdit.setValidator(QRegExpValidator(QRegExp(r"^0(\.\d{0,4})?$|^1(\.0{0,4})?$")))        # 正则表达式作输入验证
        # ^0表示以0开头，\.为字符小数点，\d为0~9的数字，{0，4}表示重复\d 0~4次，|表示或


        self.model_IoU_text = QLabel("IoU阈值")
        self.model_IoU_LineEdit = LineEdit()
        self.model_IoU_LineEdit.setText("0.7")
        self.model_IoU_LineEdit.setValidator(QRegExpValidator(QRegExp(r"^0(\.\d{0,4})?$|^1(\.0{0,4})?$")))

        self.model_imgsz_text = QLabel("图像缩放大小")
        self.model_imgsz_LineEdit = LineEdit()
        self.model_imgsz_LineEdit.setText("640")
        self.model_imgsz_LineEdit.setValidator(QRegExpValidator(QRegExp(r"^[1-9]\d{0,4}$")))

        self.model_setting_layout.addRow(self.model_path_text, self.model_path_hbox)
        self.model_setting_layout.addRow(self.model_conf_text, self.model_conf_LineEdit)
        self.model_setting_layout.addRow(self.model_IoU_text, self.model_IoU_LineEdit)
        self.model_setting_layout.addRow(self.model_imgsz_text, self.model_imgsz_LineEdit)

        # 要把组件添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addLayout(self.model_setting_layout)

        # 应用QSS
        qss_path = pathlib.Path(__file__).parent / "resource/model_setting_widget.qss"
        with open( qss_path, encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def get_model_file(self):
        model_path, _= QFileDialog.getOpenFileName(self, "打开模型文件", filter="模型文件(*.pt)")
        if model_path:
            self.model_path_LineEdit.setText(model_path)
            shared_data.model_path = model_path
            shared_data.conf = eval(self.model_conf_LineEdit.text())
            shared_data.IoU = eval(self.model_IoU_LineEdit.text())
            shared_data.imgsz = eval(self.model_imgsz_LineEdit.text())