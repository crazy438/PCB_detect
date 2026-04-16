from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QLabel, QFormLayout, QFileDialog
from qfluentwidgets import LineEdit, HeaderCardWidget

from custom_widget.line_edit import CustomLineEdit
from custom_widget.model_choose_box import ModelChooseBox
from shared_data import data

class ModelSettingWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("模型设置")
        self.headerLabel.setObjectName("model_setting_header")
        self.setBorderRadius(8)

        self.setting_layout = QFormLayout(self)

        self.model_choose_widget = ModelChooseBox(
            ("PCB缺陷检测-YOLO26", "其他"),
            ("resource/models/best.pt", None)
        )
        self.model_choose_text = QLabel("模型选择")
        self.setting_layout.addRow(self.model_choose_text, self.model_choose_widget)

        self.save_widget = CustomLineEdit("输出路径")
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
        self.imgsz_LineEdit.setText("1280")
        self.imgsz_LineEdit.setValidator(QRegExpValidator(QRegExp(r"^[1-9]\d{0,4}$")))
        self.imgsz_LineEdit.editingFinished.connect(self.update_imgsz)
        self.setting_layout.addRow(self.imgsz_text, self.imgsz_LineEdit)

        # 要把组件添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addLayout(self.setting_layout)

        # 应用QSS
        with open("resource/qss/model_setting_widget.qss", encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def get_save_path(self):
        save_path = QFileDialog.getExistingDirectory(self, "选择输出路径")
        if save_path:
            self.save_widget.line_edit.setText(save_path)
            data.save_path = save_path

    def update_conf(self):
        data.conf = eval(self.conf_LineEdit.text())

    def update_IoU(self):
        data.IoU = eval(self.IoU_LineEdit.text())

    def update_imgsz(self):
        data.imgsz = eval(self.imgsz_LineEdit.text())