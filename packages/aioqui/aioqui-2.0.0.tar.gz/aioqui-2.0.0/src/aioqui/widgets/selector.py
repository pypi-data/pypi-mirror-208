from PySide6.QtWidgets import QComboBox
from typing import Iterable, Any

from ..context import ContextObj
from ..types import Icon, QSS, Parent


class Selector(ContextObj, QComboBox):
    class Item:
        def __init__(self, text: str, icon: Icon = None, data: Any = None):
            self.params = []
            if icon:
                self.params.append(icon.icon)
            self.params.append(str(text))
            if data:
                self.params.append(data)

    def __init__(self, parent: Parent, name: str, visible: bool = True, qss: QSS = None):
        QComboBox.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        self.qss = qss

    async def init(
            self, *,
            items: Iterable[Item | str] = (),
            **kwargs
    ) -> 'Selector':
        for item in items:
            if isinstance(item, Selector.Item):
                self.addItem(*item.params)
            elif isinstance(item, str):
                self.addItem(item)
        return await self._apply(**kwargs)

    def setCurrentText(self, text: Any) -> None:
        super().setCurrentText(str(text))
