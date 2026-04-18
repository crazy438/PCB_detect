import pathlib
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import QUrl
from qfluentwidgets import HeaderCardWidget, PushButton
from qframelesswindow.webengine import FramelessWebEngineView

from custom_widget.table_widget import ResultTableWidget
from database import Database
from utils.echart import generate_analysis

class DefectStatisticsWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("缺陷统计")
        self.headerLabel.setObjectName("defect_statistics_header")
        self.setBorderRadius(8)

        self.v_box_layout = QVBoxLayout(self)

        self.web_view = FramelessWebEngineView(self)
        self.v_box_layout.addWidget(self.web_view, 2)

        # 在stackwidget后面,隐式加载会有问题,因此需要一个刷新按钮,当切换到该页面式就点击刷新
        self.refresh_button = PushButton("刷新", self)
        self.headerLayout.addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(lambda: self.web_view.load(QUrl.fromLocalFile(str(pathlib.Path("output/sample_analysis.html").absolute()))))

        self.defect_table = ResultTableWidget(["缺陷类型", "置信度", "Xmin", "Xmax", "Ymin", "Ymax"])
        self.v_box_layout.addWidget(self.defect_table, 1)

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

                # 生成样本分析图
                with Database() as db:
                    results = db.defects_statistics_query(timestamps)
                if results:
                    generate_analysis(results, html_name="output/sample_analysis.html")
                    self.web_view.load(QUrl.fromLocalFile(str(pathlib.Path("output/sample_analysis.html").absolute())))