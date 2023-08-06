from PySide6.QtGui import QFontMetrics, QPaintEvent
from PySide6.QtWidgets import QLabel

from ..types import Parent, QSS, Alignment, ElideMode, SizePolicy
from ..context import ContextObj


class Label(ContextObj, Alignment, SizePolicy, ElideMode, QLabel):
    __elide_mode: ElideMode.ElideMode
    __elide_text: str

    def __init__(self, parent: Parent, name: str, visible: bool = True, qss: QSS = None):
        QLabel.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        self.qss = qss

    async def init(
            self, *,
            wrap: bool = False, elide: ElideMode.ElideMode = None,
            **kwargs
    ) -> 'Label':
        self.__elide_mode = elide
        self.setWordWrap(wrap)
        return await self._apply(**kwargs)

    def paintEvent(self, event: QPaintEvent):
        if self.elided():
            elided_text = self.text()
            self.setText(QFontMetrics(self.font()).elidedText(elided_text, self.__elide_mode, self.width() - 10))
            self.__elide_text = elided_text
        QLabel.paintEvent(self, event)

    def elided(self) -> bool:
        return self.__elide_mode is not None

    def setText(self, text: str) -> None:
        if self.elided():
            self.__elide_text = text
        QLabel.setText(self, text)
