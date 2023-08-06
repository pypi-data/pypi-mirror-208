from PySide6.QtCore import QObject
from PySide6.QtGui import QResizeEvent
from loguru import logger
from contextlib import suppress
from PySide6.QtWidgets import (
    QPushButton, QFrame, QLabel, QLineEdit, QTextEdit, QStackedWidget, QComboBox
)

from ..types import Applicable, Event


class EventedObj:
    @staticmethod
    def Events(
            *,
            on_click: Event = None,
            on_change: Event = None,
            on_resize: Event = None,
            on_close: Event = None
    ) -> Applicable:
        async def apply(obj):
            if on_click:
                if isinstance(obj, QPushButton):
                    await EventedObj.connect(obj, 'clicked', on_click)
                elif isinstance(obj, (QLabel, QFrame)):
                    obj.mousePressEvent = lambda event: EventedObj.emit(on_click)
                else:
                    EventedObj._error(obj, 'on_click')

            if on_change:
                if isinstance(obj, (QLineEdit, QTextEdit)):
                    await EventedObj.connect(obj, 'textChanged', on_change)
                elif isinstance(obj, QStackedWidget):
                    await EventedObj.connect(obj, 'currentChanged', on_change)
                elif isinstance(obj, QComboBox):
                    await EventedObj.connect(obj, 'currentTextChanged', on_change)
                else:
                    EventedObj._error(obj, 'on_change')

            if on_close:
                def close(self) -> bool:
                    await on_close()
                    return self.close()
                obj.close = close

            if on_resize:
                def resizeEvent(self, event: QResizeEvent) -> None:
                    self.resizeEvent(self, event)
                    await on_resize()
                obj.resizeEvent = resizeEvent

            return obj
        return apply

    @staticmethod
    async def connect(obj: QObject, signalname: str, event: Event):
        signal = getattr(obj, signalname)
        with suppress(Exception):
            signal.disconnect()
        signal.connect(event)

    @staticmethod
    async def emit(event: Event) -> None:
        btn = QPushButton()
        btn.setVisible(False)
        btn.clicked.connect(event)
        btn.click()

    @staticmethod
    def _error(obj: QObject, event: str) -> None:
        logger.error(f'event `{event}` is not implemented for `{obj.objectName()}\'s` type: {type(obj)}')
