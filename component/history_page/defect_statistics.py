from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import HeaderCardWidget

from custom_widget.table_widget import ResultTableWidget
from database import Database

class DefectStatisticsWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("缺陷统计")
        self.headerLabel.setObjectName("defect_statistics_header")
        self.setBorderRadius(8)

        self.v_box_layout = QVBoxLayout(self)

        self.defect_table = ResultTableWidget(["缺陷类型", "置信度", "Xmin", "Xmax", "Ymin", "Ymax"])
        self.v_box_layout.addWidget(self.defect_table)

        # 要把组件和布局添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addLayout(self.v_box_layout)

        # 应用QSS
        with open("resource/qss/defect_statistics.qss", encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def add_results(self, timestamps):
        if timestamps:
            self.defect_table.clearContents()

            #  根据图片的处理时间查询对应的缺陷数据
            with Database() as db:
                results = db.defects_query(timestamps)
            if results:
                self.defect_table.setRowCount(len(results))
                self.setUpdatesEnabled(False)
                for i, (defect_type, conf, Xmin, Xmax, Ymin, Ymax) in enumerate(results):
                    self.defect_table.add_item(i, 0, defect_type)
                    self.defect_table.add_item(i, 1, conf)
                    self.defect_table.add_item(i, 2, Xmin)
                    self.defect_table.add_item(i, 3, Xmax)
                    self.defect_table.add_item(i, 4, Ymin)
                    self.defect_table.add_item(i, 5, Ymax)
                self.setUpdatesEnabled(True)
