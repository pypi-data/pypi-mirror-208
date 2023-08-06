from PySide6.QtWidgets import QWidget, QStackedWidget
from PySide6.QtCore import Qt

from ..objects import ContextObj


class StackedWidget(ContextObj, QStackedWidget):
    def __init__(self, parent: QWidget, name: str, visible: bool = True, stylesheet: str = None):
        QStackedWidget.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        if stylesheet:
            self.setStyleSheet(stylesheet)
            self.setAttribute(Qt.WA_StyledBackground, True)

        # workaround which includes override of `setCurrentIndex`, otherwise problems with `parent()`
        self.addWidget(QWidget(self))

    def setCurrentIndex(self, index: int) -> None:
        super().setCurrentIndex(index + 1)
