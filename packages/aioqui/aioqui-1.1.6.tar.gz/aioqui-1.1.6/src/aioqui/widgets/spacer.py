from PySide6.QtWidgets import QSpacerItem

from ..enums import SizePolicy


class Spacer(QSpacerItem):
    def __init__(self, horizontal: bool = False, vertical: bool = False):
        super().__init__(
            0, 0,
            SizePolicy.Expanding if horizontal else SizePolicy.Minimum,
            SizePolicy.Expanding if vertical else SizePolicy.Minimum
        )
