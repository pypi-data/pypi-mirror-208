from PySide6.QtCore import QObject, Qt, Signal
from contextlib import suppress
from loguru import logger
import uuid

from .contextapi import CONTEXT
from ..types import QSS, Size, Event, Icon, Parent
from src.aioqui.types.enums import Alignment, SizePolicy


class ContextObj:
    _emmitable_event: Signal = Signal()
    __blacklist: dict[str, list[str]] = {}

    def __init__(self: QObject, parent: Parent = None, name: str = str(uuid.uuid4()), visible: bool = True):
        if parent and name:
            self.setObjectName(name)
            # make `self` accessible from `parent`
            self.__register(parent, name, self)
            # make `parent` accessible from `self`
            self.__register(self, parent.objectName(), parent)
            # make `self` accessible from global `CONTEXT`
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

    def __register(self, parent: object, name: str, child: object) -> None:
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
            if hasattr(parent, name):
                delattr(parent, name)
                self.__blacklist[key].append(name)
                if CONTEXT.debug:
                    logger.warning(f'{name} already registered in {key}')
            else:
                setattr(parent, name, child)

    async def _apply(
            self: QObject,
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
            disabled: bool = None,
            qss: QSS = None,
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
        elif vpolicy or hpolicy:
            policy = self.sizePolicy()
            if vpolicy:
                policy.setVerticalPolicy(vpolicy)
            if hpolicy:
                policy.setHorizontalPolicy(hpolicy)
            self.setSizePolicy(policy)

        if alignment:
            self.setAlignment(alignment)

        if size:
            self.resize(*size)
            if width or height:
                self._size_warning()
        elif width:
            self.resize(width, self.height())
        elif height:
            self.resize(self.width(), height)

        if min_size:
            self.setMinimumSize(*min_size)
            if min_width or min_height:
                self._size_warning()
        elif min_width:
            self.setMinimumWidth(min_width)
        elif min_height:
            self.setMinimumHeight(min_height)

        if max_size:
            self.setMaximumSize(*max_size)
            if max_width or max_height:
                self._size_warning()
        elif max_width:
            self.setMaximumWidth(max_width)
        elif max_height:
            self.setMaximumHeight(max_height)

        if fixed_size:
            self.setFixedSize(*fixed_size)
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
            if hasattr(self, 'clicked'):  # QPushButton, ...
                await self._connect_event(self.clicked, on_click)
            elif hasattr(self, 'mousePressEvent'):  # QLabel, QFrame, ...
                self.mousePressEvent = lambda event: self.emit_event(on_click)
            else:
                self._event_error('on_click')

        if on_change:
            if hasattr(self, 'textChanged'):  # QLineEdit, QTextEdit, QPlainTextEdit, ...
                await self._connect_event(self.textChanged, on_change)
            elif hasattr(self, 'currentChanged'):  # QStackedWidget, ...
                await self._connect_event(self.currentChanged, on_change)
            elif hasattr(self, 'currentTextChanged'):  # QComboBox, ...
                await self._connect_event(self.currentTextChanged, on_change)
            elif hasattr(self, 'valueChanged'):  # QSlider, ...
                await self._connect_event(self.valueChanged, on_change)
            elif hasattr(self, 'dateTimeChanged'):  # QDateTimeEdit, ...
                await self._connect_event(self.dateTimeChanged, on_change)
            elif hasattr(self, 'dateChanged'):  # QDateEdit, ...
                await self._connect_event(self.dateChanged, on_change)
            elif hasattr(self, 'timeChanged'):  # QTimeEdit, ...
                await self._connect_event(self.timeChanged, on_change)
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
        :param qss:
        """
        if text:
            if hasattr(self, 'setText'):
                self.setText(text)
            elif hasattr(self, 'setCurrentText'):
                self.setCurrentText(text)
            elif hasattr(self, 'setPlainText'):
                self.setPlainText(text)

        if placeholder:
            self.setPlaceholderText(text)

        if icon:
            if hasattr(self, 'setIcon'):  # QPushButton, ...
                self.setIcon(icon.icon)
                self.setIconSize(icon.size)
            elif hasattr(self, 'setPixmap'):  # QLabel, ...
                self.setPixmap(icon.icon.pixmap(icon.size))

        if disabled:
            self.setDisabled(disabled)

        self.qss = qss

        return self

    def _size_warning(self: QObject) -> None:
        logger.warning(f'Review `{self.objectName()}.sized()` arguments')

    @staticmethod
    async def _connect_event(signal: Signal, event: Event):
        # signal.connect(slot) is faster that using getattr(self, signalName).connect(slot)
        with suppress(Exception):
            signal.disconnect()
        signal.connect(event)

    def emit_event(self, event: Event) -> None:  # created because event might be sync, async and wrapped with asyncSlot
        with suppress(Exception):
            self._emmitable_event.disconnect()
        self._emmitable_event.connect(event)
        self._emmitable_event.emit()

    def _event_error(self: QObject, event: str) -> None:
        logger.error(f'event `{event}` is not implemented for `{self.objectName()}\'s` type: {type(self)}')

    @property
    def qss(self: QObject) -> str:
        return self.styleSheet()

    @qss.setter
    def qss(self: QObject, qss: QSS) -> None:
        if qss:
            if not isinstance(qss, str):
                qss = ''.join(qss)
            self.setStyleSheet(qss)
            self.setAttribute(Qt.WA_StyledBackground, True)
