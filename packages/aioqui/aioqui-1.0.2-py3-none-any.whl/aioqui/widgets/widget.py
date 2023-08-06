from PySide6.QtWidgets import QWidget, QLayout
from PySide6.QtCore import Qt

from ..objects import ContextObj, SizedObj, EventedObj
from ..types import Applicable


class Widget(ContextObj, QWidget):
    def __init__(self, parent: QWidget, name: str, visible: bool = True, stylesheet: str = None):
        QWidget.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        if stylesheet:
            self.setAttribute(Qt.WA_StyledBackground, True)
            self.setStyleSheet(stylesheet)

    async def init(
            self, *,
            layout: QLayout = None,
            sizes: Applicable = SizedObj.Sizes(), events: Applicable = EventedObj.Events()
    ) -> 'Widget':
        if layout:
            self.setLayout(layout)
        return await sizes(await events(self))
