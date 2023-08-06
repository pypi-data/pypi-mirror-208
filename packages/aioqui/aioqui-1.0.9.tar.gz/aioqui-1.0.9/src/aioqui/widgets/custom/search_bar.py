from PySide6.QtWidgets import QWidget, QCompleter, QStyledItemDelegate
from PySide6.QtCore import Qt
from typing import Iterable

from ..line_input import LineInput
from ...types import Applicable
from ...objects import SizedObj, EventedObj


class SearchBar(LineInput):
    def __init__(self, parent: QWidget, name: str = None, visible: bool = True):
        LineInput.__init__(self, parent, name if name else self.__class__.__name__, visible)

    async def init(
            self, *,
            items: Iterable[str] = (), placeholder: str = '', stylesheet: str = '',
            sizes: Applicable = SizedObj.Sizes(), events: Applicable = EventedObj.Events()
    ) -> 'SearchBar':
        completer = QCompleter(set(items))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.popup().setObjectName(f'{self.objectName()}Popup')
        completer.popup().setItemDelegate(QStyledItemDelegate(completer))
        completer.popup().setStyleSheet(stylesheet)
        self.setStyleSheet(stylesheet)
        self.setCompleter(completer)
        await super().init(placeholder=placeholder, events=events, sizes=sizes)
        return self
