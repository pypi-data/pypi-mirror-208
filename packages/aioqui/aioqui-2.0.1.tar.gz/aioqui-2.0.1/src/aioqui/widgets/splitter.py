from PySide6.QtWidgets import QSplitter
from typing import Iterable

from .frame import Frame
from .extensions import SplitterWidgetExt
from ..context import ContextObj
from ..types import QSS, Parent, Orientation


class Splitter(ContextObj, Orientation, QSplitter):
    class Handle(Frame):
        def __init__(self, parent: Parent, name: str):
            super().__init__(parent, name, True)

    class Widget(SplitterWidgetExt, Frame):
        def __init__(self, parent: Parent, name: str, *, collapsible: bool = True,
                     expand_to: int, expand_min: int = None, expand_max: int = None):
            Frame.__init__(self, parent, name, True)
            SplitterWidgetExt.__init__(self, expand_to, expand_min, expand_max, collapsible)

    def __init__(self, parent: Parent, name: str, visible: bool = True, qss: QSS = None,
                 orientation: Orientation.Orientation = Orientation.Horizontal):
        QSplitter.__init__(self, orientation, parent)
        ContextObj.__init__(self, parent, name, visible)
        self.qss = qss

    async def init(
            self, *,
            items: Iterable[Widget] = (),
            **kwargs
    ) -> 'Splitter':
        for item in items:
            self.addWidget(item)
        return await self._apply(**kwargs)

    def addWidget(self, widget: Widget) -> None:
        super().addWidget(widget)
        widget.splitter = self
        widget.orientation = self.orientation()
        self.setCollapsible(self.count() - 1, widget.collapsible)
