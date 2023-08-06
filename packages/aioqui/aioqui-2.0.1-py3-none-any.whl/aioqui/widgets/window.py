from PySide6.QtWidgets import QMainWindow

from ..context import ContextObj
from ..types import WindowHint


class Window(ContextObj, WindowHint, QMainWindow):
    def __init__(self, name: str, stylesheet: str = None):
        QMainWindow.__init__(self)
        self.setObjectName(name)
        if stylesheet:
            self.setStyleSheet(stylesheet)

    async def init(
            self, *,
            _=...,
            **kwargs
    ) -> 'Window':
        return await self._apply(**kwargs)
