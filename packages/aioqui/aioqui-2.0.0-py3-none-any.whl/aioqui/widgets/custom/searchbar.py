from PySide6.QtWidgets import QWidget, QCompleter, QStyledItemDelegate
from PySide6.QtCore import Qt
from typing import Sequence

from ..input import LineInput


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
            completer: Completer,
            **kwargs
    ) -> 'LineInput':
        await LineInput.init(self, **kwargs)
        self.setCompleter(completer)
        return self
