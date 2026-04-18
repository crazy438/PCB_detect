from PyQt5.QtWidgets import QWidget, QHBoxLayout

from component.history_page.defect_statistics import DefectStatisticsWidget
from component.history_page.history_table import HistoryTableWidget
from database import Database

class HistoryPage(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        # QFluent要求必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))

        # 初始化数据库
        with Database() as db:
            db.init_table()

        self.h_box_layout = QHBoxLayout(self)

        self.history_table_widget = HistoryTableWidget()
        self.defect_statistics_widget = DefectStatisticsWidget()

        self.history_table_widget.history_table.emit_seletected_timestamp.connect(self.defect_statistics_widget.add_results)

        self.h_box_layout.addWidget(self.history_table_widget, 1)
        self.h_box_layout.addWidget(self.defect_statistics_widget, 2)

