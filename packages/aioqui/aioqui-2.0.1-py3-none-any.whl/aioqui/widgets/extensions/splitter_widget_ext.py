from PySide6.QtWidgets import QSplitter

from ...types import Orientation


class SplitterWidgetExt(Orientation):
    splitter: QSplitter
    __orientation: Orientation.Orientation

    def __init__(self, expand_to: int, expand_min: int = None, expand_max: int = None, collapsible: bool = True):
        self.expand_to: int = expand_to
        self.expand_min: int = expand_min
        self.expand_max: int = expand_max
        self.collapsible: bool = collapsible

    @property
    def orientation(self) -> Orientation.Orientation:
        return self.Orientation

    @orientation.setter
    def orientation(self, orientation: Orientation.Orientation) -> None:
        dimension = 'width' if orientation is Orientation.Horizontal else 'height'
        if self.expand_min:
            getattr(self, f'setMinimum{dimension.capitalize()}')(self.expand_min)
        if self.expand_max:
            getattr(self, f'setMaximum{dimension.capitalize()}')(self.expand_max)
        self.__orientation = orientation

    def _index(self) -> int:
        for index in range(self.splitter.count()):
            if self == self.splitter.widget(index):
                return index
        raise IndexError(f'{self} not found in {self.splitter} widgets')

    def _set_size(self, size: int):
        index = self._index()
        self.splitter.setSizes([*self.splitter.sizes()[:index], size, *self.splitter.sizes()[index + 1:]])

    def expand(self, size: int = None):
        if not self.splitter.sizes()[self._index()]:
            self._set_size(size if size else self.expand_to)

    def shrink(self, size: int = None) -> None:
        self._set_size(size if size else 0)

    def toggle(self, shrink_to: int = None, expand_to: int = None) -> None:
        if self.splitter.sizes()[self._index()]:
            self.shrink(shrink_to)
        else:
            self.expand(expand_to)
