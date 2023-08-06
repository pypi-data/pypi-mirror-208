from PySide6.QtWidgets import QScrollArea, QWidget
from PySide6.QtCore import QObject
from typing import Sequence, Iterable

from .frame import Frame
from .layout import Layout
from ..objects import ContextObj, SizedObj, EventedObj
from ..enums import Orientation, ScrollPolicy
from ..types import Applicable


class ScrollArea(ContextObj, ScrollPolicy, Orientation, QScrollArea):
    def __init__(self, parent: QWidget, name: str, visible: bool = True, stylesheet: str = None):
        QScrollArea.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        if stylesheet:
            self.setStyleSheet(stylesheet)

    async def init(
            self, *,
            orientation: Orientation.Orientation,
            hpolicy: ScrollPolicy.ScrollPolicy = ScrollPolicy.WhenNeeded,
            vpolicy: ScrollPolicy.ScrollPolicy = ScrollPolicy.WhenNeeded,

            margins: tuple[int, ...] = (0, 0, 0, 0), spacing: int = 0, alignment: Layout.Alignment = None,
            items: Sequence[QObject] = (),
            sizes: Applicable = SizedObj.Sizes(), events: Applicable = EventedObj.Events()
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
        return await sizes(await events(self))

    def clear(self, exceptions: Iterable[QObject] = ()):
        self.widget().layout().clear(exceptions)
