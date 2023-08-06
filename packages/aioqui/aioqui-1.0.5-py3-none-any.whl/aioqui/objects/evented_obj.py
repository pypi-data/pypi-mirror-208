from PySide6.QtCore import QObject
from loguru import logger
from contextlib import suppress
from PySide6.QtWidgets import (
    QPushButton, QFrame, QLabel, QLineEdit, QTextEdit, QStackedWidget, QComboBox
)

from ..types import Applicable, Event
from ..qasyncio import asyncSlot


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
                if isinstance(QLineEdit, QTextEdit):
                    await EventedObj.connect(obj, 'textChanged', on_change)
                elif isinstance(obj, QStackedWidget):
                    await EventedObj.connect(obj, 'currentChanged', on_change)
                elif isinstance(obj, QComboBox):
                    await EventedObj.connect(obj, 'currentTextChanged', on_change)
                else:
                    EventedObj._error(obj, 'on_change')

            if on_close:
                async def close(self) -> bool:
                    await self.on_close()
                    return super.close(obj)
                obj.close = close
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
        logger.error(f'event `{event}` is not implemented for `{obj.objectName()}\'s` type')
