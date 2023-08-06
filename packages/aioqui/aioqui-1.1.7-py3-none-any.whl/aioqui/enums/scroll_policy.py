from PySide6.QtCore import Qt


class ScrollPolicy:
    ScrollPolicy = Qt.ScrollBarPolicy

    AlwaysOn = Qt.ScrollBarPolicy.ScrollBarAlwaysOn
    AlwaysOff = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    WhenNeeded = Qt.ScrollBarPolicy.ScrollBarAsNeeded
    