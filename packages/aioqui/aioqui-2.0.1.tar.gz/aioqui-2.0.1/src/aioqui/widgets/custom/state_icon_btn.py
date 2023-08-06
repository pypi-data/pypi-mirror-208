from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QIcon
from typing import Callable

from ..button import Button
from ...types import Icon
from ...qasyncio import asyncSlot


class StateIconButton(Button):
    def __init__(self, parent: QWidget, name: str = None, visible: bool = True, state: bool = False):
        super().__init__(parent, name if name else self.__class__.__name__, visible)
        self.__state: bool = state
        self.if_set_icon: Icon = Icon('star-fill.svg', (30, 30))
        self.if_unset_icon: Icon = Icon('star.svg', (30, 30))

    async def init(
            self, *,
            if_set_icon: Icon = None, if_unset_icon: Icon = None, pre_slot: Callable[..., bool],
            **kwargs
    ) -> 'StateIconButton':
        if if_unset_icon:
            self.setIcon(QIcon(if_unset_icon.icon))
            self.setIconSize(if_unset_icon.size)
        if if_set_icon:
            self.if_set_icon = if_set_icon
        if if_unset_icon:
            self.if_unset_icon = if_unset_icon
        return await Button.init(self, on_click=lambda: self.__mainevent(pre_slot), **kwargs)

    @asyncSlot()
    async def __mainevent(self, pre_slot: Callable[..., bool]) -> None:
        # toggle to change state
        self.state = not self.state
        if not await pre_slot():
            # toggle once more to come back to prev state if `pre_slot` returns `False`
            self.state = not self.state

    @property
    def state(self) -> bool:
        return self.__state

    @state.setter
    def state(self, state: bool) -> None:
        if state:
            self.setIcon(self.if_set_icon.icon)
            self.setIconSize(self.if_set_icon.size)
        else:
            self.setIcon(self.if_unset_icon.icon)
            self.setIconSize(self.if_unset_icon.size)
        self.__state = state
