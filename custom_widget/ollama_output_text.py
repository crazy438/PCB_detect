from qfluentwidgets import setFont, PlainTextEdit


class OllamaOutputText(PlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        setFont(self, 20)

    def append_text(self, text):
        cursor = self.textCursor()
        cursor.insertText(text)
        self.setTextCursor(cursor)