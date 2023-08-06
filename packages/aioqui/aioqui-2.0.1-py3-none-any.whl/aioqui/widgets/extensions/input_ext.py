from PySide6.QtWidgets import QTextEdit, QLineEdit, QPlainTextEdit

from ...types import EchoMode


class InputExt(EchoMode):
    def setText(self, text: str) -> None:
        if isinstance(self, QLineEdit):
            QLineEdit.setText(self, text)
        elif isinstance(self, QTextEdit):
            QTextEdit.setText(self, text)
        elif isinstance(self, QPlainTextEdit):
            QPlainTextEdit.setPlainText(self, text)

    def text(self) -> str:
        if isinstance(self, QLineEdit):
            return QLineEdit.text(self)
        if isinstance(self, QTextEdit):
            return QTextEdit.toPlainText(self)
        if isinstance(self, QPlainTextEdit):
            return QPlainTextEdit.toPlainText(self)
