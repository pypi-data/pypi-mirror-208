from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import QSize

from ..frame import Frame
from ..label import Label
from ..layout import Layout
from ...types import Icon


# ToDo: fix setVisible and objectName for outer and inner object (maybe using inheritance from Label setting Layout)
class LabelExtended(Frame):
    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        Frame.__init__(self, parent, f'{name}Frame', visible)
        self.__name = name

    async def init(
            self, *,
            text: str = '', inner_alignment: Label.Alignment = None, wrap: bool = False, size: QSize = None,
            icon: Icon = None, elided: bool = False, policy: tuple[QSizePolicy, QSizePolicy] = None,
            margins: tuple[int, ...] = (0, 0, 0, 0), outer_alignment: Layout.Alignment = None
    ) -> 'LabelExtended':
        await super().init(layout=await Layout.horizontal().init(
            margins=margins, alignment=outer_alignment,
            items=[
                label := await Label(self.parent(), self.__name).init(
                    text=text, alignment=inner_alignment, wrap=wrap, size=size, icon=icon, elided=elided, policy=policy
                )
            ]
        ))
        self.label = label
        return self
