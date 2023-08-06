from PySide6.QtCore import QObject
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
                    with suppress(Exception):
                        self.clicked.disconnect()
                    self.clicked.connect(on_click)
                elif isinstance(self, (QLabel, QFrame)):
                    self.mousePressEvent = lambda event: EventedObj.emit(on_click)
                else:
                    EventedObj.error(self, 'on_click')

            if on_change:
                if isinstance(QLineEdit, QTextEdit):
                    with suppress(Exception):
                        self.textChanged.disconnect()
                    self.textChanged.connect(on_change)
                elif isinstance(self, QStackedWidget):
                    with suppress(Exception):
                        self.currentChanged.disconnect()
                    self.currentChanged.connect(on_change)
                elif isinstance(self, QComboBox):
                    self.currentTextChanged.connect(on_change)
                else:
                    EventedObj.error(self, 'on_change')

            return self
        return apply

    @staticmethod
    async def emit(event: EventType):
        btn = QPushButton()
        btn.setVisible(False)
        btn.clicked.connect(event)
        btn.click()

    @staticmethod
    def error(handler: QObject, event: str) -> str:
        raise NotImplementedError(f'{handler.objectName()} is undefined handler for `{event}` event')
