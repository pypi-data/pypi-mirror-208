from PySide6.QtWidgets import QComboBox, QWidget
from typing import Iterable, Any

from ..objects import ContextObj, SizedObj, EventedObj
from ..types import Applicable, Icon


class Selector(ContextObj, QComboBox):
    class Item:
        def __init__(self, text: str, icon: Icon = None, data: Any = None):
            self.params = []
            if icon:
                self.params.append(icon)
            self.params.append(str(text))
            if data:
                self.params.append(data)

    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QComboBox.__init__(self)
        ContextObj.__init__(self, parent, name, visible)

    async def init(
            self, *,
            items: Iterable[Item | str] = (),
            sizes: Applicable = SizedObj.Sizes(), events: Applicable = EventedObj.Events()
    ) -> 'Selector':
        for item in items:
            if isinstance(item, Selector.Item):
                self.addItem(*item.params)
            elif isinstance(item, str):
                self.addItem(item)
        return await sizes(await events(self))

    def setCurrentText(self, text: Any) -> None:
        super().setCurrentText(str(text))
