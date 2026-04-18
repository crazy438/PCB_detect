from qfluentwidgets import HeaderCardWidget, PushButton, FluentIcon

from custom_widget.history_table import HistoryTable

class HistoryTableWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("历史记录")
        self.headerLabel.setObjectName("history_table_header")
        self.setBorderRadius(8)

        self.history_table = HistoryTable(["时间戳", "时间", "文件路径", "模型名称", "缺陷数量"])

        self.delete_button = PushButton(FluentIcon.DELETE, "删除")
        self.delete_button.clicked.connect(self.history_table.delete_selected_rows)
        self.headerLayout.addWidget(self.delete_button)

        self.clear_button = PushButton(FluentIcon.DELETE, "清空")
        self.clear_button.clicked.connect(self.history_table.clear)
        self.headerLayout.addWidget(self.clear_button)

        # 要把组件和布局添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addWidget(self.history_table)

        # 应用QSS
        with open("resource/qss/history_table.qss", encoding='utf-8') as f:
            self.setStyleSheet(f.read())