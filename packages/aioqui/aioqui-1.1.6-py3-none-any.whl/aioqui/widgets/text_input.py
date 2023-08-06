from PySide6.QtWidgets import QTextEdit, QWidget

from ..objects import ContextObj, SizedObj, EventedObj
from ..types import Applicable


class TextInput(ContextObj, QTextEdit):
    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QTextEdit.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)

    async def init(
            self, *,
            placeholder: str = '', text: str = '',
            sizes: Applicable = SizedObj.Sizes(), events: Applicable = EventedObj.Events()
    ) -> 'TextInput':
        self.setText(text)
        self.setPlaceholderText(placeholder)
        return await sizes(await events(self))
