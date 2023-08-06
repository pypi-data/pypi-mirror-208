from PySide6.QtWidgets import QWidget
from typing import Callable, Awaitable


Applicable = Callable[[QWidget], Awaitable]
