from PySide6.QtWidgets import QLineEdit, QWidget

from ..objects import ContextObj, SizedObj, EventedObj
from ..types import Applicable


class LineInput(ContextObj, QLineEdit):
    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QLineEdit.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)

    async def init(
            self, *,
            placeholder: str = '', text: str = '', hidden: bool = False,
            sizes: Applicable = SizedObj.applicable_sizes(), events: Applicable = EventedObj.applicable_events()
    ) -> 'LineInput':
        self.setText(text)
        self.setPlaceholderText(placeholder)
        if hidden:
            self.hide_echo()
        return await sizes(await events(self))

    def hide_echo(self):
        self.setEchoMode(QLineEdit.EchoMode.Password)

    def show_echo(self):
        self.setEchoMode(QLineEdit.EchoMode.Normal)

    def toggle_echo(self):
        self.hide_echo() if self.echoMode() == QLineEdit.EchoMode.Normal else self.show_echo()
