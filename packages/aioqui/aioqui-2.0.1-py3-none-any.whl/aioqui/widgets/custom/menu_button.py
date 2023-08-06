from PySide6.QtWidgets import QWidget

from ..button import Button
from ..label import Label
from ..layout import Layout
from ...types import Icon, Size


class MenuButton(Button):
    IconBtn: Button
    TextLbl: Label
    TotalLbl: Label

    def __init__(self, parent: QWidget, name: str = None, visible: bool = True):
        super().__init__(parent, name if name else self.__class__.__name__, visible)

    async def init(
            self, *,
            icon: Icon, text: str, total: int = 0,
            **kwargs
    ) -> 'MenuButton':
        self.setLayout(await Layout.horizontal().init(
            margins=(10, 5, 10, 5), spacing=10,
            items=[
                IconBtn := await Button(self, f'{self.objectName()}IconBtn').init(
                    icon=icon, disabled=True, fixed_size=Size(icon.size.width(), icon.size.height())
                ), Layout.Left,
                TextLbl := await Label(self, f'{self.objectName()}TextLbl').init(
                    text=text, hpolicy=Label.Expanding, elide=Label.ElideRight
                ),
                TotalLbl := await Label(self, f'{self.objectName()}TotalLbl').init(
                    text=str(total)
                ), Layout.Right
            ]
        ))
        self.IconBtn = IconBtn
        self.TextLbl = TextLbl
        self.TotalLbl = TotalLbl
        return await Button.init(self, **kwargs)
