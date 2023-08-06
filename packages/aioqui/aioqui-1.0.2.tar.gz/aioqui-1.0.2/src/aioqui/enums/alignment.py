from PySide6.QtCore import Qt


class Alignment:
    Alignment = Qt.AlignmentFlag

    Left = Qt.AlignLeft
    LeftTop = Qt.AlignLeft | Qt.AlignTop
    LeftCenter = Qt.AlignLeft | Qt.AlignVCenter
    LeftBottom = Qt.AlignLeft | Qt.AlignBottom
    Right = Qt.AlignRight
    RightTop = Qt.AlignRight | Qt.AlignTop
    RightCenter = Qt.AlignRight | Qt.AlignVCenter
    RightBottom = Qt.AlignRight | Qt.AlignBottom
    VCenter = Qt.AlignVCenter
    HCenter = Qt.AlignHCenter
    Top = Qt.AlignTop
    TopCenter = Qt.AlignHCenter | Qt.AlignTop
    Bottom = Qt.AlignBottom
    BottomCenter = Qt.AlignHCenter | Qt.AlignBottom
    Center = Qt.AlignHCenter | Qt.AlignVCenter
