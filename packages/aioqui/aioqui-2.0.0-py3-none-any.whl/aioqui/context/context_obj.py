from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QFrame, QLineEdit, QTextEdit, QPlainTextEdit, QStackedWidget, QComboBox, QSlider
)
from PySide6.QtCore import QObject, Qt
from contextlib import suppress
from loguru import logger
import uuid

from .contextapi import CONTEXT
from ..types import QSS, Size, Event, Icon
from ..enums import Alignment, SizePolicy


class ContextObj:
    __blacklist: dict[str, list[str]] = {}

    def __init__(self, parent: QWidget = None, name: str = str(uuid.uuid4()), visible: bool = True):
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
                logger.warning(f"{self.__class__.__name__} not registered in `ContextAPI` since {' and '.join(attributes)} not specified")

        with suppress(Exception):
            self.setVisible(visible)

    def __register(self, parent: object, name: str, child: QWidget) -> None:
        """
        Check if object not in `blacklist`, then register, otherwise show warning
        Check if object already registered, push its name to `blacklist` unregister and show warning, otherwise register
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
                    logger.warning(f'{name} already registered in {key}')
            except AttributeError:
                setattr(parent, name, child)

    async def _apply(
            self,
            *,
            # Sizes
            policy: tuple[SizePolicy.SizePolicy, SizePolicy.SizePolicy] = None,
            vpolicy: SizePolicy.SizePolicy = None,
            hpolicy: SizePolicy.SizePolicy = None,

            # margins: ? = ?,
            # padding: ? = ?,
            alignment: Alignment.Alignment = None,

            size: Size = None,
            width: int = None,
            height: int = None,

            min_size: Size = None,
            min_width: int = None,
            min_height: int = None,

            max_size: Size = None,
            max_width: int = None,
            max_height: int = None,

            fixed_size: Size = None,
            fixed_width: int = None,
            fixed_height: int = None,

            # Events
            on_click: Event = None,
            on_change: Event = None,
            on_close: Event = None,
            on_resize: Event = None,

            # Common
            text: str = None,
            placeholder: str = None,
            icon: Icon = None,
            disabled: bool = None
    ) -> 'ContextObj':
        """
        :param policy:
        :param vpolicy:
        :param hpolicy:
        :param alignment:
        :param size:
        :param width:
        :param height:
        :param min_size:
        :param min_width:
        :param min_height:
        :param max_size:
        :param max_width:
        :param max_height:
        :param fixed_size:
        :param fixed_width:
        :param fixed_height:
        """
        if policy:
            self.setSizePolicy(*policy)
            if vpolicy or hpolicy:
                self._size_warning()
        else:
            policy = self.sizePolicy()
            if vpolicy:
                policy.setVerticalPolicy(vpolicy)
            elif hpolicy:
                policy.setHorizontalPolicy(hpolicy)
            self.setSizePolicy(policy)

        if alignment:
            self.setAlignment(alignment)

        if size:
            self.resize(*size.size)
            if width or height:
                self._size_warning()
        elif width:
            self.resize(width, self.height())
        elif height:
            self.resize(self.width(), height)

        if min_size:
            self.setMinimumSize(*min_size.size)
            if min_width or min_height:
                self._size_warning()
        elif min_width:
            self.setMinimumWidth(min_width)
        elif min_height:
            self.setMinimumHeight(min_height)

        if max_size:
            self.setMaximumSize(*max_size.size)
            if max_width or max_height:
                self._size_warning()
        elif max_width:
            self.setMaximumWidth(max_width)
        elif max_height:
            self.setMaximumHeight(max_height)

        if fixed_size:
            self.setFixedSize(*fixed_size.size)
            if fixed_width or fixed_height:
                self._size_warning()
        elif fixed_width:
            self.setFixedWidth(fixed_width)
        elif fixed_height:
            self.setFixedHeight(fixed_height)
        """
        :param on_click:
        :param on_change:
        :param on_close:
        :param on_resize:
        """
        if on_click:
            if isinstance(self, QPushButton):
                await self._connect_str_signal('clicked', on_click)
            elif isinstance(self, (QLabel, QFrame)):
                self.mousePressEvent = lambda event: self._emit(on_click)
            else:
                self._event_error('on_click')

        if on_change:
            if isinstance(self, (QLineEdit, QTextEdit, QPlainTextEdit)):
                await self._connect_str_signal('textChanged', on_change)
            elif isinstance(self, QStackedWidget):
                await self._connect_str_signal('currentChanged', on_change)
            elif isinstance(self, QComboBox):
                await self._connect_str_signal('currentTextChanged', on_change)
            elif isinstance(self, QSlider):
                await self._connect_str_signal('valueChanged', on_change)
            else:
                self._event_error('on_change')

        # if on_close:
        #     def close(self) -> bool:
        #         print(self)
        #         rv = self.close()
        #         self.emit(on_close)
        #         return rv
        #     obj.close = close
        #
        # if on_resize:
        #     async def resizeEvent(self, event: QResizeEvent) -> None:
        #         self.resizeEvent(self, event)
        #         await on_resize()
        #     obj.resizeEvent = lambda event: self.emit(lambda: resizeEvent(event))

        """
        :param text:
        :param placeholder:
        :param icon:
        :param disabled:
        """
        if text:
            self.setText(text)
        if placeholder:
            self.setPlaceholderText(text)
        if icon:
            if isinstance(self, QPushButton):
                self.setIcon(icon.icon)
                self.setIconSize(icon.size)
            elif isinstance(self, QLabel):
                self.setPixmap(icon.icon.pixmap(icon.size))
        if disabled:
            self.setDisabled(disabled)
        return self

    def _size_warning(self: QObject) -> None:
        logger.warning(f'Review `{self.objectName()}.sized()` arguments')

    async def _connect_str_signal(self: QObject, signal: str, event: Event):
        signal = getattr(self, signal)
        with suppress(Exception):
            signal.disconnect()
        signal.connect(event)

    @staticmethod
    def _emit(event: Event) -> None:
        # _emit created and used because event might be sync, async and async wrapped with asyncSlot
        btn = QPushButton()
        btn.setVisible(False)
        btn.clicked.connect(event)
        btn.click()
        btn.deleteLater()

    def _event_error(self: QObject, event: str) -> None:
        logger.error(f'event `{event}` is not implemented for `{self.objectName()}\'s` type: {type(self)}')

    @property
    def qss(self) -> str:
        return self.styleSheet()

    @qss.setter
    def qss(self, qss: QSS) -> None:
        if qss:
            if not isinstance(qss, str):
                qss = ''.join(qss)
            self.setStyleSheet(qss)
            self.setAttribute(Qt.WA_StyledBackground, True)
