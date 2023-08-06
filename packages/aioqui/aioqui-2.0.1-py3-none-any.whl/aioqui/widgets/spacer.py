from PySide6.QtWidgets import QSpacerItem

from ..types import SizePolicy


class Spacer(SizePolicy, QSpacerItem):
    def __init__(self, hpolicy: SizePolicy.SizePolicy, vpolicy: SizePolicy.SizePolicy):
        QSpacerItem.__init__(self, 0, 0, hpolicy, vpolicy)
