from PySide6.QtWidgets import QStackedWidget, QFrame
from PySide6.QtCore import QObject
from typing import Iterable

from ..context import ContextObj
from ..types import QSS, Parent, Alignment, Orientation


class StackedWidget(ContextObj, Orientation, QStackedWidget):
    def __init__(self, parent: Parent, name: str, visible: bool = True, qss: QSS = None):
        QStackedWidget.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        self.qss = qss

        # workaround which includes override of `setCurrentIndex`, otherwise problems with `parent()`
        self.addWidget(QFrame(self))  # QFrame is likely the most lightweight QWidget in Qt6

    async def init(
            self, *,
            alignment: Alignment.Alignment = Alignment.HCenter, items: Iterable[QObject] = (),
            **kwargs
    ) -> 'StackedWidget':
        self.layout().setAlignment(alignment)
        for item in items:
            self.addWidget(item)
        return await self._apply(**kwargs)

    def setCurrentIndex(self, index: int) -> None:
        super().setCurrentIndex(index + 1)
