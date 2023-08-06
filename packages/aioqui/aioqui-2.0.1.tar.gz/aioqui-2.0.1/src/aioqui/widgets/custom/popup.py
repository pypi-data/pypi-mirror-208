from PySide6.QtGui import QResizeEvent
from qasync import asyncSlot
from typing import Iterable

from .. import Frame, Layout, Button, Label
from ...types import Parent, Event, DefaultEvent, QSS, LogicButton


class Popup(LogicButton, Frame):
    def __init__(self, parent: Parent, name: str = None, qss: QSS = None, *,
                 message: str = '', buttons: Iterable[LogicButton] = (LogicButton.YES, LogicButton.NO),
                 on_success: Event = DefaultEvent, on_failure: Event = DefaultEvent):
        super().__init__(parent, name if name else self.__class__.__name__)
        self.qss = qss
        self.message: str = message
        self.buttons: Iterable[LogicButton] = buttons
        self.on_success: Event = on_success
        self.on_failure: Event = on_failure
        self.hide()

    @asyncSlot()
    async def display(self) -> None:
        self.setLayout(await Layout.vertical().init(
            spacing=10, alignment=Layout.Center, margins=(20, 20, 20, 20),
            items=[
                await Frame(self, f'{self.objectName()}Frame').init(
                    layout=await Layout.vertical().init(
                        spacing=20, margins=(20, 20, 20, 20),
                        items=[
                            await Label(self, f'{self.objectName()}MessageLbl').init(
                                text=self.message, wrap=True, alignment=Layout.Center
                            ),
                            await Layout.horizontal().init(
                                spacing=20,
                                items=[
                                    await Button(self, f'{self.objectName()}YesBtn', Popup.YES in self.buttons).init(
                                        text='Yes', on_click=lambda: self.__mainevent(self.on_success)
                                    ),
                                    await Button(self, f'{self.objectName()}NoBtn', Popup.NO in self.buttons).init(
                                        text='No', on_click=lambda: self.__mainevent(self.on_failure)
                                    ),
                                    await Button(self, f'{self.objectName()}OkBtn', Popup.OK in self.buttons).init(
                                        text='Ok', on_click=lambda: self.__mainevent(self.on_success)
                                    ),
                                    await Button(self, f'{self.objectName()}CancelBtn', Popup.CANCEL in self.buttons).init(
                                        text='Cancel', on_click=lambda: self.__mainevent(self.on_failure)
                                    )
                                ]
                            )
                        ]
                    )
                )
            ]
        ))
        self.show()

    @asyncSlot()
    async def __mainevent(self, event: Event):
        self.emit_event(event)
        self.deleteLater()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.resize(self.parent().size())
