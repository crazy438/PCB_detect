from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from qfluentwidgets import TableWidget
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QAbstractItemView
from shared_data import data

class CustomTableWidget(TableWidget):
    def __init__(self, row_count, colum_count, header_labels, parent=None):
        super().__init__(parent)
        self.setBorderVisible(True)
        self.setBorderRadius(8)
        self.setWordWrap(False)
        self.setSelectionBehavior(QAbstractItemView.SelectRows) # 单击选中整行
        self.setSelectionMode(QAbstractItemView.SingleSelection) # 一次只能选中一行，不允许选中多行
        self.setEditTriggers(QAbstractItemView.NoEditTriggers) # 禁止编辑
        self.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                font-size: 20px;
                font-family: 'Microsoft YaHei';
                color: black;
            }
        """)
        self.verticalHeader().hide()
        self.setRowCount(row_count)
        self.setColumnCount(colum_count)
        self.setHorizontalHeaderLabels(header_labels)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def add_item(self, i, j, text):
        item = QTableWidgetItem(str(text))
        item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        item.setFont(QFont("Microsoft YaHei", 14))
        self.setItem(i, j, item)

    def add_item_from_results(self, current_row, img_path):
        if data.result_table_items:
            self.clearContents()
            labels, confs, coordinates = data.result_table_items[current_row]
            for i, label in enumerate(labels):
                self.add_item(i, 0, label)
            for i, conf in enumerate(confs):
                self.add_item(i, 1, conf)
            for i, (Xmin, Xmax, Ymin, Ymax) in enumerate(coordinates):
                self.add_item(i, 2, Xmin)
                self.add_item(i, 3, Xmax)
                self.add_item(i, 4, Ymin)
                self.add_item(i, 5, Ymax)