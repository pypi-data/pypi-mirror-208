from PySide6.QtWidgets import QFrame, QLayout

from ..types import QSS, Parent
from ..context import ContextObj


class Frame(ContextObj, QFrame):
    def __init__(self, parent: Parent, name: str, visible: bool = True, qss: QSS = None):
        QFrame.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        self.qss = qss

    async def init(
            self, *,
            style: ... = None, layout: QLayout = None,
            **kwargs,
    ) -> 'Frame':
        if style:
            self.setFrameStyle(style)
        if layout:
            self.setLayout(layout)
        return await self._apply(**kwargs)
