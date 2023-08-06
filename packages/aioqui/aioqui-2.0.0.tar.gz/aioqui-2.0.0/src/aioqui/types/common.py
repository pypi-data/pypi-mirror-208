from PySide6.QtWidgets import QWidget
from typing import Callable, Awaitable, Iterable, Optional


Event = Callable[..., Awaitable]
Parent = QWidget
QSS = Optional[str | Iterable[str]]
