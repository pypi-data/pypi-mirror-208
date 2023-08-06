from PySide6.QtCore import QSettings as _QSettings
from loguru import logger
import socket as _socket
from typing import Any


class ContextAPI:  # create warning when instance is reassigned
    __settings = _QSettings(_socket.gethostname(), __file__)
    debug: bool = False

    def __getitem__(self, key: str) -> Any:
        return self.__settings.value(key)

    def __setitem__(self, key: str, value: Any) -> None:
        return self.__settings.setValue(key, value)


CONTEXT: ContextAPI = ContextAPI()
