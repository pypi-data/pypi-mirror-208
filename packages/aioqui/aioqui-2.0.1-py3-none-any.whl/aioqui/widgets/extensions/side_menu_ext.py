from ...types import Orientation


class SideMenuExt:
    def __init__(self, expand_to: int, expand_orientation: Orientation.Orientation):
        self.expand_to: int = expand_to
        self.__expand_orientation: Orientation.Orientation = expand_orientation

    def __size(self):
        return self.width() if self.__expand_orientation is Orientation.Horizontal else self.height()

    def expand(self, expand_to: int = None):
        if expand_to:
            self.expand_to = expand_to
        self.setFixedWidth(self.expand_to)

    def shrink(self) -> None:
        self.setFixedWidth(0)

    def toggle(self) -> None:
        self.expand() if self.__size() == 0 else self.shrink()
