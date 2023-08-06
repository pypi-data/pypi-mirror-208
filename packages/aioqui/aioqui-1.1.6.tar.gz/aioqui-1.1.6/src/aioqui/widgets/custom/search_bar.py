from PySide6.QtWidgets import QWidget, QCompleter, QStyledItemDelegate
from PySide6.QtCore import Qt
from typing import Sequence

from ..line_input import LineInput
from ...types import Applicable
from ...objects import SizedObj, EventedObj


class SearchBar(LineInput):
    class Completer(QCompleter):
        def __init__(self, parent: QWidget, *, items: Sequence[str], stylesheet: str = ''):
            super().__init__(items, parent)
            self.setCaseSensitivity(Qt.CaseInsensitive)
            self.popup().setObjectName(f'{parent.objectName()}Popup')
            self.popup().setItemDelegate(QStyledItemDelegate(self))
            self.popup().setStyleSheet(stylesheet)

    def __init__(self, parent: QWidget, name: str = None, visible: bool = True):
        LineInput.__init__(self, parent, name if name else self.__class__.__name__, visible)

    async def init(
            self, *,
            placeholder: str, completer: Completer, hidden: bool = False,
            sizes: Applicable = SizedObj.Sizes(), events: Applicable = EventedObj.Events()
    ) -> 'LineInput':
        await super().init(placeholder=placeholder, hidden=hidden, events=events, sizes=sizes)
        self.setCompleter(completer)
        return self
