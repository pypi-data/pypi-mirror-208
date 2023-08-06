from PySide6.QtWidgets import QWidget
from typing import Callable, Awaitable, Any


Applicable = Callable[[QWidget], Awaitable]
Event = Callable[..., Awaitable]
