from PySide6.QtWidgets import QWidget
from typing import Callable, Awaitable, Iterable, Optional, Any, Union


Parent: type = QWidget
QSS: type = Optional[str | Iterable[str]]
Event = Callable[..., Union[Awaitable, Any]]
DefaultEvent = lambda: None
