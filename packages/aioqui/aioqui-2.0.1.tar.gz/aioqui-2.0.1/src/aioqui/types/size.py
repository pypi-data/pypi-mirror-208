class Size:
    def __init__(self, width: int = ..., height: int = ...):
        self.w: int = width if width is not Ellipsis else None
        self.h: int = height if height is not Ellipsis else None

    @property
    def size(self):
        return self.w, self.h

    def __iter__(self):
        yield from self.size
