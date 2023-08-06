from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout
from typing import Union
from abc import ABC

from ..types import Parent, Alignment, Orientation
from .extensions import LayoutExt
from ..context import ContextObj


class VerticalLayout(ContextObj, LayoutExt, QVBoxLayout):
    def __init__(self, parent: Parent = None, name: str = None):
        QVBoxLayout.__init__(self, parent)
        ContextObj.__init__(self, parent, name, True)


class HorizontalLayout(ContextObj, LayoutExt, QHBoxLayout):
    def __init__(self, parent: Parent = None, name: str = None):
        QHBoxLayout.__init__(self, parent)
        ContextObj.__init__(self, parent, name, True)


class Layout(ABC, Alignment, Orientation):
    @staticmethod
    def horizontal(parent: Parent = None, name: str = None) -> HorizontalLayout:
        return HorizontalLayout(parent, name)

    @staticmethod
    def vertical(parent: Parent = None, name: str = None) -> VerticalLayout:
        return VerticalLayout(parent, name)

    @staticmethod
    def oriented(
            orientation: Orientation.Orientation, parent: Parent = None, name: str = None
    ) -> Union[VerticalLayout, HorizontalLayout]:
        return Layout.vertical(parent, name) if orientation is Orientation.Vertical else Layout.horizontal(parent, name)
