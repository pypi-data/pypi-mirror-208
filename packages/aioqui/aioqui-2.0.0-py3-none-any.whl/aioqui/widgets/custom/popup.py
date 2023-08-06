from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QMessageBox
from qasync import asyncSlot
from typing import Iterable

from .. import Widget, Layout, Button, Label, Frame
from ...types import Parent


class Popup(Widget):
    YES = QMessageBox.StandardButton.Yes
    NO = QMessageBox.StandardButton.No
    OK = QMessageBox.StandardButton.Ok
    CANCEL = QMessageBox.StandardButton.Cancel

    stylesheet = f'''
        #Popup {{
            background-color: rgba(255, 255, 255, 0.1);
        }}

        #PopupFrame {{
            background-color: #17212B;
            min-width: 400px;
            min-height: 200px;
            border-radius: 20px;
        }}

        #PopupMessageLbl {{
            color: white;
            font-size: 24px;
            background-color: transparent;
        }}

        #PopupOkBtn,
        #PopupCancelBtn,
        #PopupYesBtn,
        #PopupNoBtn {{
            color: white;
            border: none;
            font-size: 18px; 
            border-radius: 5px;
            min-height: 40px;
        }}

        #PopupOkBtn,
        #PopupYesBtn {{
            background-color: darkgreen;
        }}
    
        #PopupOkBtn:hover,
        #PopupYesBtn:hover {{
            background-color: rgba(0, 255, 0, 0.5);
        }}
        
        #PopupCancelBtn,
        #PopupNoBtn {{
            background-color: rgba(182, 0, 40, 1);
        }}

        #PopupCancelBtn:hover,
        #PopupNoBtn:hover {{
            background-color: rgba(182, 0, 40, 0.5);
        }}
        '''

    def __init__(self, parent: Parent, name: str = None, stylesheet: str = stylesheet):
        super().__init__(parent, name if name else self.__class__.__name__, True, stylesheet)

    @asyncSlot()
    async def display(
            self, *,
            message: str = '', buttons: Iterable = (),
            on_success: callable = lambda: None, on_failure: callable = lambda: None
    ) -> 'Popup':
        if not buttons:
            buttons = [Popup.YES, Popup.NO]
        btns = []
        if Popup.YES in buttons:
            btns.append(await Button(self, f'{self.objectName()}YesBtn').init(
                text='Yes', on_click=lambda: self.slot(on_success)
            ))
        if Popup.NO in buttons:
            btns.append(await Button(self, f'{self.objectName()}NoBtn').init(
                text='No', on_click=lambda: self.slot(on_failure)
            ))
        if Popup.OK in buttons:
            btns.append(await Button(self, f'{self.objectName()}OkBtn').init(
                text='Ok', on_click=lambda: self.slot(on_success)
            ))
        if Popup.CANCEL in buttons:
            btns.append(await Button(self, f'{self.objectName()}CancelBtn').init(
                text='Cancel', on_click=lambda: self.slot(on_failure)
            ))

        self.setLayout(await Layout.vertical().init(
            spacing=10, alignment=Layout.Center, margins=(20, 20, 20, 20),
            items=[
                await Frame(self, f'{self.objectName()}Frame').init(
                    layout=await Layout.vertical().init(
                        spacing=20, margins=(20, 20, 20, 20),
                        items=[
                            await Label(self, f'{self.objectName()}MessageLbl').init(
                                text=message, wrap=True, alignment=Layout.Center
                            ),
                            await Layout.horizontal().init(
                                spacing=20, items=btns
                            )
                        ]
                    )
                )
            ]
        ))
        return self

    @asyncSlot()
    async def slot(self, slot: callable):
        slot()
        self.deleteLater()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.resize(self.parent().size())
