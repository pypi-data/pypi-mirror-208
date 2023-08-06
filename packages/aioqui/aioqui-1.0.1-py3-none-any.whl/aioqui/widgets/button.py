from PySide6.QtWidgets import QPushButton, QWidget
from PySide6.QtGui import QIcon

from ..objects import ContextObj, SizedObj, EventedObj
from ..types import Applicable, Icon


class Button(ContextObj, QPushButton):
    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QPushButton.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)

    async def init(
            self, *,
            text: str = '', icon: Icon = None, disabled: bool = False,
            sizes: Applicable = SizedObj.applicable_sizes(), events: Applicable = EventedObj.applicable_events()
    ) -> 'Button':
        self.setText(text)
        self.setDisabled(disabled)
        if icon:
            self.setIcon(QIcon(icon.icon))
            self.setIconSize(icon.size)
        return await sizes(await events(self))
