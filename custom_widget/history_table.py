import time
from PyQt5.QtCore import pyqtSignal, QTimer

from custom_widget.message_box import TipMessageBox
from custom_widget.table_widget import ResultTableWidget

from database import Database

class HistoryTable(ResultTableWidget):
    emit_seletected_timestamp = pyqtSignal(str)
    def __init__(self, header_labels, parent=None):
        super().__init__(header_labels, parent)
        self.hideColumn(0)
        self.currentCellChanged.connect(lambda index: self.emit_seletected_timestamp.emit(self.item(index, 0).text() if self.item(index, 0) else ""))
        self.flush_history_table()

    def flush_history_table(self):
        self.clearContents()
        with Database() as db:
            history = db.imgs_query()
        if history:
            self.setRowCount(len(history))
            for i, (timestamp, img_path, model, n_defects) in enumerate(history):
                process_time = time.strftime("%Y年%m月%d日%H时%M分%S秒", time.localtime(timestamp/1000))
                self.add_item(i, 0, timestamp)
                self.add_item(i, 1, process_time)
                self.add_item(i, 2, img_path)
                self.add_item(i, 3, model)
                self.add_item(i, 4, n_defects)

        # 延迟10ms切换索引, 给控件渲染时间
        QTimer.singleShot(10, lambda: self.setCurrentCell(0,0))

    def delete_selected_rows(self):
        selected_rows = self.selectionModel().selectedRows()
        if selected_rows:
            w = TipMessageBox("是否真的要删除?", '删除的数据无法恢复!', self.window())
            w.cancelButton.show()
            if w.exec():
                selected_rows.sort(reverse=True) # 要逆序删除,从后往前删
                timestamps_to_delete = [self.item(row.row(), 0).text() for row in selected_rows]
                for row in selected_rows:
                    self.removeRow(row.row())
                with Database() as db:
                    db.delete_rows(timestamps_to_delete)

    def clear(self):
        w = TipMessageBox("是否真的要清空数据?", '删除的数据无法恢复!', self.window())
        w.cancelButton.show()
        if w.exec():
            self.clearContents()
            with Database() as db:
                db.clear()
