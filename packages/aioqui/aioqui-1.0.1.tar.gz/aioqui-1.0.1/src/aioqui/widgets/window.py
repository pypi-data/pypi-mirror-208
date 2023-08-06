from PySide6.QtWidgets import QMainWindow

from ..enums import WindowHint


class Window(WindowHint, QMainWindow):
    def __init__(self, name: str, stylesheet: str = None):
        QMainWindow.__init__(self)
        self.setObjectName(name)
        if stylesheet:
            self.setStyleSheet(stylesheet)

    async def init(self) -> 'Window':
        return self
