from PySide6.QtWidgets import QStatusBar

from ..context import ContextObj
from ..types import Parent


class StatusBar(ContextObj, QStatusBar):
    def __init__(self, parent: Parent, name: str, visible: bool = True):
        QStatusBar.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
