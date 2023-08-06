from PySide6.QtWidgets import QSlider
from PySide6.QtCore import Qt

from ..context import ContextObj
from ..types import Parent, Orientation


class Slider(ContextObj, Orientation, QSlider):
    def __init__(self, parent: Parent, name: str, visible: bool = True,
                 orientation: Orientation.Orientation = Orientation.Horizontal):
        QSlider.__init__(self, orientation, parent)
        ContextObj.__init__(self, parent, name, visible)

    async def init(
            self, *,
            step: int, value: int,
            **kwargs
    ) -> 'Slider':
        self.setFocusPolicy(Qt.StrongFocus)
        self.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.setTickInterval(10)
        self.setSingleStep(step)
        self.setValue(value)
        return await self.apply(**kwargs)
