from PySide6.QtWidgets import QWidget, QStackedWidget
from PySide6.QtCore import Qt, QObject
from typing import Iterable

from ..objects import ContextObj, SizedObj, EventedObj
from ..enums import Alignment
from ..types import Applicable


class StackedWidget(ContextObj, QStackedWidget):
    def __init__(self, parent: QWidget, name: str, visible: bool = True, stylesheet: str = None):
        QStackedWidget.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        if stylesheet:
            self.setStyleSheet(stylesheet)
            self.setAttribute(Qt.WA_StyledBackground, True)

        # workaround which includes override of `setCurrentIndex`, otherwise problems with `parent()`
        self.addWidget(QWidget(self))

    async def init(
            self, *,
            alignment: Alignment.Alignment = Alignment.HCenter, items: Iterable[QObject] = (),
            sizes: Applicable = SizedObj.Sizes(), events: Applicable = EventedObj.Events()
    ) -> 'StackedWidget':
        self.layout().setAlignment(alignment)
        for item in items:
            self.addWidget(item)
        return await sizes(await events(self))

    def setCurrentIndex(self, index: int) -> None:
        super().setCurrentIndex(index + 1)
