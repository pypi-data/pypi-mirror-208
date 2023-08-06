from PySide6.QtWidgets import QScrollArea
from PySide6.QtCore import QObject
from typing import Sequence, Iterable

from .frame import Frame
from .layout import Layout
from ..context import ContextObj
from ..types import QSS, Parent, Orientation, ScrollPolicy


class ScrollArea(ContextObj, ScrollPolicy, Orientation, QScrollArea):
    def __init__(self, parent: Parent, name: str, visible: bool = True, qss: QSS = None):
        QScrollArea.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        self.qss = qss

    async def init(
            self, *,
            orientation: Orientation.Orientation,
            hpolicy: ScrollPolicy.ScrollPolicy = ScrollPolicy.WhenNeeded,
            vpolicy: ScrollPolicy.ScrollPolicy = ScrollPolicy.WhenNeeded,

            margins: tuple[int, ...] = (0, 0, 0, 0), spacing: int = 0, alignment: Layout.Alignment = None,
            items: Sequence[QObject] = (),

            **kwargs
    ) -> 'ScrollArea':
        self.setHorizontalScrollBarPolicy(hpolicy)
        self.setVerticalScrollBarPolicy(vpolicy)
        self.setWidgetResizable(True)
        frame = Frame(self, f'{self.objectName()}Widget')
        self.setWidget(await frame.init(
            layout=await Layout.oriented(orientation, frame, f'{frame.objectName()}Layout').init(
                margins=margins, spacing=spacing, alignment=alignment, items=items
            )
        ))
        return await self._apply(**kwargs)

    def addWidget(self, widget: Parent) -> None:
        self.widget().layout().addWidget(widget)

    def clear(self, exceptions: Iterable[QObject] = ()):
        self.widget().layout().clear(exceptions)
