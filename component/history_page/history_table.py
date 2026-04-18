import time

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QFont
from qfluentwidgets import HeaderCardWidget, PushButton, FluentIcon, MessageBox

from custom_widget.message_box import TipMessageBox
from custom_widget.table_widget import ResultTableWidget
from database import Database


class HistoryTableWidget(HeaderCardWidget):
    emit_seletected_timestamp = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("历史记录")
        self.headerLabel.setObjectName("history_table_header")
        self.setBorderRadius(8)

        self.delete_button = PushButton(FluentIcon.DELETE, "删除")
        self.delete_button.setObjectName("delete_button")
        self.headerLayout.addWidget(self.delete_button)


        self.history_table = ResultTableWidget(10, ["时间戳", "时间", "文件路径", "模型名称", "缺陷数量"])
        self.history_table.hideColumn(0)
        self.history_table.currentCellChanged.connect(lambda index: self.emit_seletected_timestamp.emit(self.history_table.item(index, 0).text() if self.history_table.item(index, 0) else ""))
        self.delete_button.clicked.connect(self.delete_selected_rows)
        self.flush_history_table()

        # 要把组件和布局添加到HeaderCardWidget的viewLayout才会显示
        self.viewLayout.addWidget(self.history_table)

        # 应用QSS
        with open("resource/qss/history_table.qss", encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def flush_history_table(self):
        self.history_table.clearContents()
        with Database() as db:
            history = db.imgs_query()
        if history:
            for i, (timestamp, img_path, model, n_defects) in enumerate(history):
                process_time = time.strftime("%Y年%m月%d日%H时%M分%S秒", time.localtime(timestamp/1000))
                self.history_table.add_item(i, 0, timestamp)
                self.history_table.add_item(i, 1, process_time)
                self.history_table.add_item(i, 2, img_path)
                self.history_table.add_item(i, 3, model)
                self.history_table.add_item(i, 4, n_defects)

        # 延迟10ms切换索引, 给控件渲染时间
        QTimer.singleShot(10, lambda: self.history_table.setCurrentCell(0,0))

    def delete_selected_rows(self):
        selected_rows = self.history_table.selectionModel().selectedRows()
        if selected_rows:
            w = TipMessageBox("是否真的要删除?", '删除的数据无法恢复!', self.window())
            w.cancelButton.show()
            if w.exec():
                selected_rows.sort(reverse=True) # 要逆序删除,从后往前删
                timestamps_to_delete = [self.history_table.item(row.row(), 0).text() for row in selected_rows]
                for row in selected_rows:
                    self.history_table.removeRow(row.row())
                with Database() as db:
                    db.delete_rows(timestamps_to_delete)


