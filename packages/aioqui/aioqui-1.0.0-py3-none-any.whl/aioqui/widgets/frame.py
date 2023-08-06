from PySide6.QtWidgets import QFrame, QWidget, QLayout

from ..objects import ContextObj, SizedObj, EventedObj
from ..types import Applicable


class Frame(ContextObj, QFrame):
    def __init__(self, parent: QWidget, name: str, visible: bool = True, stylesheet: str = None):
        QFrame.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        if stylesheet:
            self.setStyleSheet(stylesheet)

    async def init(
            self, *,
            style: ... = None, layout: QLayout = None,
            sizes: Applicable = SizedObj.applicable_sizes(), events: Applicable = EventedObj.applicable_events()
    ) -> 'Frame':
        if style:
            self.setFrameStyle(style)
        if layout:
            self.setLayout(layout)
        return await sizes(await events(self))
