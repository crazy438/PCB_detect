from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import TableWidget, setCustomStyleSheet
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QAbstractItemView, QDialog, QVBoxLayout, QLabel


class ResultTableWidget(TableWidget):
    def __init__(self, header_labels, parent=None):
        super().__init__(parent)
        self.setBorderVisible(True)
        self.setBorderRadius(8)
        self.setSelectionBehavior(QAbstractItemView.SelectRows) # 单击选中整行
        self.setSelectionMode(QAbstractItemView.SingleSelection) # 一次只能选中一行，不允许选中多行
        self.setEditTriggers(QAbstractItemView.NoEditTriggers) # 禁止编辑
        self.verticalHeader().hide()
        self.setColumnCount(len(header_labels))
        self.setHorizontalHeaderLabels(header_labels)
        self.setWordWrap(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_qss = """
                QHeaderView::section {
                    font-size: 20px;
                    font-family: 'Microsoft YaHei';
                    color: black;
                 }
        """
        setCustomStyleSheet(self, table_qss, table_qss)

    def add_item(self, i, j, text):
        text=str(text)
        item = QTableWidgetItem(text)
        item.setToolTip(text)
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        item.setFont(QFont("Microsoft YaHei", 14))
        self.setItem(i, j, item)