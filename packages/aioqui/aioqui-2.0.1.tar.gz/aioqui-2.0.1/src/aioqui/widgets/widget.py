from PySide6.QtWidgets import QWidget, QLayout

from ..context import ContextObj
from ..types import QSS


class Widget(ContextObj, QWidget):
    def __init__(self, parent: QWidget, name: str, visible: bool = True, qss: QSS = None):
        QWidget.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        self.qss = qss

    async def init(
            self, *,
            layout: QLayout = None,
            **kwargs
    ) -> 'Widget':
        if layout:
            self.setLayout(layout)
        return await self._apply(**kwargs)
