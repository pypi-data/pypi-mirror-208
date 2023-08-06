from PySide6.QtWidgets import QPushButton

from ..types import Parent, QSS
from ..context import ContextObj


class Button(ContextObj, QPushButton):
    def __init__(self, parent: Parent, name: str, visible: bool = True, qss: QSS = None):
        QPushButton.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        self.qss = qss

    async def init(
            self, *,
            _=...,
            **kwargs
    ) -> 'Button':
        return await self._apply(**kwargs)
