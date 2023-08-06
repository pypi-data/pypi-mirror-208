from PySide6.QtWidgets import QSizePolicy


class SizePolicy:
    SizePolicy = QSizePolicy

    Default = QSizePolicy.Policy.Ignored
    Expanding = QSizePolicy.Policy.Expanding
    Minimum = QSizePolicy.Policy.Minimum
    Maximum = QSizePolicy.Policy.Maximum
