from PySide6.QtWidgets import QWidget
from loguru import logger as _logger
from contextlib import suppress as _suppress
from typing import Iterable
import uuid

from ..contextapi import CONTEXT
from .sized_obj import SizedObj
from .evented_obj import EventedObj


class ContextObj(SizedObj, EventedObj):
    __blacklist: dict[str, list[str]] = {}

    def __init__(self, parent: QWidget = None, name: str = str(uuid.uuid4()), visible: bool = True,
                 stylesheet: str | Iterable[str] = None):
        if parent and name:
            self.setObjectName(name)
            self.__register(parent, name, self)
            self.__register(self, parent.objectName(), parent)
            self.__register(CONTEXT, name, self)

            self.core = parent
            while p := self.core.parent():
                self.core = p
        else:
            attributes = []
            if not parent:
                attributes.append('`parent`')
            if not name:
                attributes.append('`name`')
            if CONTEXT.debug:
                _logger.warning(f"{self.__class__.__name__} not registered in `ContextAPI` since {' and '.join(attributes)} not specified")

        with _suppress(Exception):
            self.setVisible(visible)
        if stylesheet:
            with _suppress(Exception):
                if not isinstance(stylesheet, str):
                    stylesheet = ''.join(stylesheet)
                self.setStyleSheet(stylesheet)

    def __register(self, parent: object, name: str, child: QWidget) -> None:
        """
        Check if object not in `blacklist`, then register, otherwise show warning
        Check if object already registered, push its name to `blacklist` unregister and show warning otherwise register
        :param parent:
        :param name:
        :param child:
        :return:
        """
        key = parent.__class__.__name__
        self.__blacklist[key] = self.__blacklist.get(key, [])
        if name not in self.__blacklist[key]:
            try:
                getattr(parent, name)
                delattr(parent, name)
                self.__blacklist[key].append(name)
                if CONTEXT.debug:
                    _logger.warning(f'{name} already registered in {key}')
            except AttributeError:
                setattr(parent, name, child)
