from PySide6.QtGui import QIcon
from contextlib import suppress

from ..button import Button
from .popup import Popup
from ...types import Icon, Size, Parent, Event, DefaultEvent
from ...qasyncio import asyncSlot
from ...misc import fileops
from ..qss.popup import qss


class ImageButton(Button):
    RemoveBtn: Button

    bytes = None

    def __init__(self, parent: Parent, name: str = None, visible: bool = True):
        super().__init__(parent, name if name else self.__class__.__name__, visible)

    async def init(
            self, *,
            on_success: Event = DefaultEvent, directory: str = '',
            **kwargs
    ) -> 'ImageButton':
        await super().init(on_click=lambda: self.choose_image(on_success, directory), **kwargs)
        self.RemoveBtn = await Button(self, f'{self.objectName()}RemoveBtn').init(
            icon=Icon('x-circle.svg', (30, 30)), fixed_size=Size(30, 30),
            on_click=Popup(self.core, qss=qss, message=f'Remove image?', on_success=self.remove_image).display
        )
        self.RemoveBtn.move(self.width() - 30, 0)
        self.RemoveBtn.setStyleSheet(f'''
            #{self.objectName()}RemoveBtn {{background-color: transparent; border-radius: 14px;}}
            #{self.objectName()}RemoveBtn:hover {{background-color: rgba(255, 255, 255, 0.3);}}
        ''')
        return self

    def remove_image(self):
        super().setIcon(QIcon())
        self.bytes = None
        with suppress(AttributeError):
            self.RemoveBtn.setVisible(False)
        print('cl')

    def setIcon(self, icon: QIcon) -> None:
        self.bytes = Icon.bytes(icon, self.iconSize())
        super().setIcon(icon)
        with suppress(AttributeError):
            self.RemoveBtn.setVisible(True)

    def setDisabled(self, disabled: bool) -> None:
        with suppress(AttributeError):
            self.RemoveBtn.setVisible(not disabled)
        super().setDisabled(disabled)

    def setEnabled(self, enabled: bool) -> None:
        with suppress(AttributeError):
            self.RemoveBtn.setVisible(enabled)
        super().setEnabled(enabled)

    @asyncSlot()
    async def choose_image(self, on_success: Event, directory: str = ''):
        if filepath := await fileops.select_file(self, 'Choose image', directory, 'Images (*.jpg)'):
            with open(filepath, 'rb') as file:
                self.setIcon(Icon(file.read()).icon)
            on_success()
