from PySide6.QtWidgets import QSlider, QWidget

from ..objects import ContextObj
from ..enums import Orientation


class Slider(ContextObj, Orientation, QSlider):
    def __init__(self, parent: QWidget, name: str, visible: bool = True):
        QSlider.__init__(self, parent)
        ContextObj.__init__(self, parent, name, visible)
    #
    # async def init(
    #         self, *,
    #         orientation: OrientationExt.Orientation, step: int = 1,
    #         on_change: callable = None
    # ) -> 'Slider':
    #     self.setFocusPolicy(Qt.StrongFocus)
    #     self.setTickPosition(QSlider.TicksBothSides)
    #     self.setTickInterval(10)
    #     self.setSingleStep(10)
    #     self.setValue(self.controls.get(display=display))
    #     if on_change:
    #         self.valueChanged.connect(lambda: self.controls.set(display=display, value=slider.value()))
    #     return self
