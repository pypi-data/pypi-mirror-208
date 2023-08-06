from PySide6.QtWidgets import QMainWindow

from ..objects import SizedObj, EventedObj
from ..enums import WindowHint
from ..types import Applicable


class Window(WindowHint, QMainWindow):
    def __init__(self, name: str, stylesheet: str = ''):
        QMainWindow.__init__(self)
        self.setObjectName(name)
        self.setStyleSheet(stylesheet)

    async def init(
            self, *,
            sizes: Applicable = SizedObj.Sizes(), events: Applicable = EventedObj.Events()
    ) -> 'Window':
        return await sizes(await events(self))
