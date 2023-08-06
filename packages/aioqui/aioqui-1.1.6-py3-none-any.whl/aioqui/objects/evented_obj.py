from PySide6.QtCore import QObject
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
            # on_resize: Event = None,
            # on_close: Event = None
    ) -> Applicable:
        async def apply(obj):
            if on_click:
                if isinstance(obj, QPushButton):
                    await EventedObj._connect(obj, 'clicked', on_click)
                elif isinstance(obj, (QLabel, QFrame)):
                    obj.mousePressEvent = lambda event: EventedObj._emit(on_click)
                else:
                    EventedObj._error(obj, 'on_click')

            if on_change:
                if isinstance(obj, (QLineEdit, QTextEdit)):
                    await EventedObj._connect(obj, 'textChanged', on_change)
                elif isinstance(obj, QStackedWidget):
                    await EventedObj._connect(obj, 'currentChanged', on_change)
                elif isinstance(obj, QComboBox):
                    await EventedObj._connect(obj, 'currentTextChanged', on_change)
                else:
                    EventedObj._error(obj, 'on_change')

            # if on_close:
            #     def close(self) -> bool:
            #         print(self)
            #         rv = self.close()
            #         EventedObj.emit(on_close)
            #         return rv
            #     obj.close = close
            #
            # if on_resize:
            #     async def resizeEvent(self, event: QResizeEvent) -> None:
            #         self.resizeEvent(self, event)
            #         await on_resize()
            #     obj.resizeEvent = lambda event: EventedObj.emit(lambda: resizeEvent(event))

            return obj
        return apply

    @staticmethod
    async def _connect(obj: QObject, signalname: str, event: Event):
        signal = getattr(obj, signalname)
        with suppress(Exception):
            signal.disconnect()
        signal.connect(event)

    @staticmethod
    def _emit(event: Event) -> None:
        btn = QPushButton()
        btn.setVisible(False)
        btn.clicked.connect(event)
        btn.click()
        btn.deleteLater()

    @staticmethod
    def _error(obj: QObject, event: str) -> None:
        logger.error(f'event `{event}` is not implemented for `{obj.objectName()}\'s` type: {type(obj)}')
