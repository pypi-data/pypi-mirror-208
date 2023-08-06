from PySide6.QtGui import QFontMetrics, QPaintEvent
from PySide6.QtWidgets import QLabel, QWidget

from ..misc import Icon
from ..objects import ContextObj, SizedObj, EventedObj
from ..enums import Alignment, ElideMode
from ..types import Applicable


class Label(ContextObj, Alignment, ElideMode, QLabel):
    __elide = ElideMode.ElideNone
    __elide_text = ''

    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QLabel.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)

    def paintEvent(self, event: QPaintEvent):
        if elide_mode := self.__elide:
            elided_text = self.__elide_text
            self.setText(QFontMetrics(self.font()).elidedText(elided_text, elide_mode, self.width() - 10))
            self.__elide_text = elided_text
        super().paintEvent(event)

    async def init(
            self, *,
            text: str = '', wrap: bool = False, icon: Icon = None, elide: ElideMode.ElideMode = ElideMode.ElideNone,
            sizes: Applicable = SizedObj.applicable_sizes(), events: Applicable = EventedObj.applicable_events()
    ) -> 'Label':
        self.__elide, self.__elide_text = elide, text
        self.setText(text)
        self.setWordWrap(wrap)
        if icon:
            self.setPixmap(icon.icon.pixmap(icon.size))
        return await sizes(await events(self))

    def setText(self, text: str) -> None:
        if self.__elide:
            self.__elide_text = text
        super().setText(text)
