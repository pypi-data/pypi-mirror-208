from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from typing import Union
from abc import ABC

from .extensions import LayoutExt
from ..objects import ContextObj
from ..enums import Alignment, SizePolicy, Orientation


class Layout(ABC, Alignment, SizePolicy, Orientation):
    @classmethod
    def horizontal(cls, parent: QWidget = None, name: str = None) -> 'HLayout':
        return HLayout(parent, name)

    @classmethod
    def vertical(cls, parent: QWidget = None, name: str = None) -> 'VLayout':
        return VLayout(parent, name)

    @classmethod
    def oriented(cls, orientation: Qt.Orientation, parent: QWidget = None, name: str = None) -> Union['VLayout', 'HLayout']:
        return Layout.vertical(parent, name) if orientation is Layout.Vertical else Layout.horizontal(parent, name)


class VLayout(ContextObj, LayoutExt, QVBoxLayout):
    def __init__(self, parent: QWidget = None, name: str = None):
        QVBoxLayout.__init__(self, parent)
        ContextObj.__init__(self, parent, name, True)


class HLayout(ContextObj, LayoutExt, QHBoxLayout):
    def __init__(self, parent: QWidget = None, name: str = None):
        QHBoxLayout.__init__(self, parent)
        ContextObj.__init__(self, parent, name, True)
