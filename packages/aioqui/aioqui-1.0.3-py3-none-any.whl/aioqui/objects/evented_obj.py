from PySide6.QtCore import QObject
from loguru import logger
from contextlib import suppress
from PySide6.QtWidgets import (
    QPushButton, QFrame, QLabel, QLineEdit, QTextEdit, QStackedWidget, QComboBox
)

from ..types import Applicable


class EventedObj:
    EventType = type[callable]

    @staticmethod
    def Events(
            *,
            on_click: EventType = None,
            on_change: EventType = None,
            # on_resize: EventType = None  # ?
    ) -> Applicable:
        async def apply(self):
            if on_click:
                if isinstance(self, QPushButton):
                    await EventedObj.connect(self, 'clicked', on_click)
                elif isinstance(self, (QLabel, QFrame)):
                    self.mousePressEvent = lambda event: EventedObj.emit(on_click)
                else:
                    EventedObj._error(self, 'on_click')

            if on_change:
                if isinstance(QLineEdit, QTextEdit):
                    await EventedObj.connect(self, 'textChanged', on_change)
                elif isinstance(self, QStackedWidget):
                    await EventedObj.connect(self, 'currentChanged', on_change)
                elif isinstance(self, QComboBox):
                    await EventedObj.connect(self, 'currentTextChanged', on_change)
                else:
                    EventedObj._error(self, 'on_change')

            return self
        return apply

    @staticmethod
    async def connect(obj: QObject, signalname: str, event: EventType):
        signal = getattr(obj, signalname)
        with suppress(Exception):
            signal.disconnect()
        signal.connect(event)

    @staticmethod
    async def emit(event: EventType):
        btn = QPushButton()
        btn.setVisible(False)
        btn.clicked.connect(event)
        btn.click()

    @staticmethod
    def _error(handler: QObject, event: str) -> None:
        logger.error(f'{handler.objectName()} is undefined handler for `{event}` event')
