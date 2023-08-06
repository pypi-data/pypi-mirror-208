from PySide6.QtCore import QPropertyAnimation, Property
from time import sleep

from ...misc import ConditionalThreadQueue
from ..label import Label
from ...qasyncio import asyncSlot
from ...types import Parent


class ErrorLabel(Label):
    __duration: float = 0.5
    __ctq: ConditionalThreadQueue = ConditionalThreadQueue()

    def __init__(self, parent: Parent, name: str = None, visible: bool = True):
        super().__init__(parent, name if name else self.__class__.__name__, visible)

    async def init(
            self, *,
            _=None,
            **kwargs
    ) -> 'ErrorLabel':
        return await Label.init(self, **kwargs)

    def setText(self, text: str, delay: float = 2, duration: int = 0.5) -> None:
        if delay == 0:  # if delay is 0, just set the text
            return Label.setText(self, '')

        if not text:  # text == '' means instantly clear the text and hide label without `post` action
            self.setVisible(False)
            return Label.setText(self, '')

        def pre():
            self._set_opacity(1)
            Label.setText(self, text)
            self.setVisible(True)
            sleep(delay)

        def post():
            self.emit_event(self.reduce)

        self.__duration = duration
        self.__ctq.new(pre, post)

    @asyncSlot()
    async def reduce(self):
        self.animation = QPropertyAnimation(self, b"_opacity")
        self.animation.setDuration(int(self.__duration * 1000))
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.start()

    def _get_opacity(self):
        return self.__opacity

    def _set_opacity(self, opacity: float):
        self.__opacity = opacity
        self.setStyleSheet(f'color: rgba(255, 0, 0, {opacity});')

    __opacity: float = 1
    _opacity: Property = Property(float, _get_opacity, _set_opacity)
