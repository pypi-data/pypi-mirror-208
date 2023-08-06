from PySide6.QtWidgets import QStatusBar, QWidget

from ..objects import ContextObj


class StatusBar(ContextObj, QStatusBar):
    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QStatusBar.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)

    async def init(self) -> 'StatusBar':
        return self
