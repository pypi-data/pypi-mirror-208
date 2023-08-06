from PySide6.QtWidgets import QWidget, QLayoutItem, QSpacerItem
from PySide6.QtCore import Qt, QObject
from typing import Sequence, Iterable

from ...types import Alignment


class LayoutExt(Alignment):
    async def init(
            self, *,
            margins: tuple[int, ...] = (0, 0, 0, 0), spacing: int = 0, alignment: Qt.Alignment = None,
            items: Sequence[QObject] = ()
    ) -> 'LayoutExt':
        self.setContentsMargins(*margins)
        self.setSpacing(spacing)
        if alignment:
            self.setAlignment(alignment)
        self.add_items(items)
        return self

    def add(self, obj: QObject, alignment: Qt.AlignmentFlag = None) -> QObject:
        if isinstance(obj, QWidget):
            if alignment:
                self.addWidget(obj, alignment=alignment)
            else:
                self.addWidget(obj)
        elif isinstance(obj, QSpacerItem):
            self.addSpacerItem(obj)
        elif isinstance(obj, QLayoutItem):
            self.addLayout(obj)
        else:
            raise TypeError(f'{obj} has unsupported type {type(obj)} to `add` to {self}')
        return obj

    def add_items(self, items: Sequence[QObject]):
        i = 0
        while i < len(items):
            if i + 1 < len(items) and isinstance(items[i + 1], (Qt.AlignmentFlag, Qt.Alignment)):
                self.add(items[i], items[i + 1])
                i += 1
            else:
                self.add(items[i])
            i += 1

    def clear(self, exceptions: Iterable[QObject] = ()):
        for i in reversed(range(self.count())):
            layout_item = self.itemAt(i).widget()
            if not layout_item:
                layout_item = self.itemAt(i).layout()
            if not layout_item:
                layout_item = self.itemAt(i).spacerItem()
            if layout_item not in exceptions:
                layout_item.setParent(None)
