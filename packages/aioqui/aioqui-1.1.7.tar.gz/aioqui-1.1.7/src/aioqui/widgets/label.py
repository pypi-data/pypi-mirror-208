from PySide6.QtGui import QFontMetrics, QPaintEvent
from PySide6.QtWidgets import QLabel, QWidget

from ..objects import ContextObj, SizedObj, EventedObj
from ..enums import Alignment, ElideMode
from ..types import Applicable, Icon


class Label(ContextObj, Alignment, ElideMode, QLabel):
    __elide_mode: ElideMode.ElideMode
    __elide_text: str

    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QLabel.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)

    async def init(
            self, *,
            text: str = '', wrap: bool = False, icon: Icon = None, elide: ElideMode.ElideMode = None,
            sizes: Applicable = SizedObj.Sizes(), events: Applicable = EventedObj.Events()
    ) -> 'Label':
        self.__elide_mode, self.__elide_text = elide, text
        self.setText(text)
        self.setWordWrap(wrap)
        if icon:
            self.setPixmap(icon.icon.pixmap(icon.size))
        return await sizes(await events(self))

    def paintEvent(self, event: QPaintEvent):
        if self.elided():
            elided_text = self.__elide_text
            self.setText(QFontMetrics(self.font()).elidedText(elided_text, self.__elide_mode, self.width() - 10))
            self.__elide_text = elided_text
        super().paintEvent(event)

    def elided(self) -> bool:
        return self.__elide_mode is not None

    def setText(self, text: str) -> None:
        if self.elided():
            self.__elide_text = text
        super().setText(text)
