from PySide6.QtWidgets import QLineEdit, QTextEdit, QPlainTextEdit
from abc import ABC

from ..types import QSS, Parent, EchoMode
from .extensions import InputExt
from ..context import ContextObj


class LineInput(ContextObj, InputExt, QLineEdit):
    def __init__(self, parent: Parent, name: str, visible: bool = True, qss: QSS = None):
        QLineEdit.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        self.qss = qss

    async def init(
            self, *,
            hidden: bool = False,
            **kwargs
    ) -> 'LineInput':
        if hidden:
            self.hide_echo()
        return await self._apply(**kwargs)

    def hide_echo(self):
        self.setEchoMode(EchoMode.Hidden)

    def show_echo(self):
        self.setEchoMode(EchoMode.Default)

    def toggle_echo(self):
        self.hide_echo() if self.echoMode() == EchoMode.Default else self.show_echo()


class ReachInput(ContextObj, InputExt, QTextEdit):
    def __init__(self, parent: Parent, name: str, visible: bool = True, qss: QSS = None):
        QTextEdit.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        self.qss = qss

    async def init(
            self, *,
            _,
            **kwargs
    ) -> 'ReachInput':
        return await self._apply(**kwargs)


class PlainInput(ContextObj, InputExt, QPlainTextEdit):
    def __init__(self, parent: Parent, name: str, visible: bool = True, qss: QSS = None):
        QPlainTextEdit.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
        self.qss = qss

    async def init(
            self, *,
            _,
            **kwargs
    ) -> 'PlainInput':
        return await self._apply(**kwargs)


class Input(ABC, EchoMode):
    @staticmethod
    def line(parent: Parent, name: str, visible: bool = True, qss: QSS = None) -> LineInput:
        return LineInput(parent, name, visible, qss)

    @staticmethod
    def reach(parent: Parent, name: str, visible: bool = True, qss: QSS = None) -> ReachInput:
        return ReachInput(parent, name, visible, qss)

    @staticmethod
    def plain(parent: Parent, name: str, visible: bool = True, qss: QSS = None) -> PlainInput:
        return PlainInput(parent, name, visible, qss)
