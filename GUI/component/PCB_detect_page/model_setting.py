import pathlib
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QFormLayout, QFileDialog, QLineEdit
from qfluentwidgets import PushButton, LineEdit, HeaderCardWidget, FluentIcon

from GUI.component import shared_data

class ModelSettingWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("模型设置")
        self.headerLabel.setObjectName("model_setting_header")
        self.setBorderRadius(8)

        self.setting_layout = QFormLayout(self)

        self.path_widget = CustomLineEdit("模型路径")
        self.path_widget.button.clicked.connect(self.get_model_path)
        self.setting_layout.addRow(self.path_widget.text, self.path_widget.hbox)

        self.save_widget = CustomLineEdit("结果保存路径")
        self.save_widget.button.clicked.connect(self.get_save_path)
        self.setting_layout.addRow(self.save_widget.text, self.save_widget.hbox)

        self.conf_text = QLabel("置信度阈值")
        self.conf_LineEdit = LineEdit()
        self.conf_LineEdit.setText("0.25")
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
        self.imgsz_LineEdit.setText("640")
        self.imgsz_LineEdit.setValidator(QRegExpValidator(QRegExp(r"^[1-9]\d{0,4}$")))
        self.imgsz_LineEdit.editingFinished.connect(self.update_imgsz)
        self.setting_layout.addRow(self.imgsz_text, self.imgsz_LineEdit)

        # 要把组件添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addLayout(self.setting_layout)

        # 应用QSS
        qss_path = pathlib.Path(__file__).parent / "resource/model_setting_widget.qss"
        with open( qss_path, encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def get_model_path(self):
        model_path, _= QFileDialog.getOpenFileName(self, "打开模型文件", filter="模型文件(*.pt)")
        if model_path:
            self.path_widget.line_edit.setText(model_path)
            shared_data.model_path = model_path
            shared_data.is_changed = True

    def get_save_path(self):
        save_path = QFileDialog.getExistingDirectory(self, "选择输出路径")
        if save_path:
            self.save_widget.line_edit.setText(save_path)
            shared_data.save_path = save_path
            shared_data.is_changed = True

    def update_conf(self):
        shared_data.conf = eval(self.conf_LineEdit.text())
        shared_data.is_changed = True

    def update_IoU(self):
        shared_data.IoU = eval(self.IoU_LineEdit.text())
        shared_data.is_changed = True

    def update_imgsz(self):
        shared_data.imgsz = eval(self.imgsz_LineEdit.text())
        shared_data.is_changed = True

class CustomLineEdit(LineEdit):
    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.text = QLabel(label_text)
        self.line_edit = LineEdit()
        self.line_edit.setReadOnly(True)

        self.button = PushButton(FluentIcon.FOLDER, "浏览")

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.line_edit)
        self.hbox.addWidget(self.button)