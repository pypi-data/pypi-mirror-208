from PySide6.QtCore import QPropertyAnimation, Property, QObject
from typing import Any, Callable

from ..qasyncio import asyncSlot


async def create(  # uncompleted
        obj: QObject,
        pname: str,
        ptype: type,
        duration: float,
        vrange: tuple[Any, Any],
        getter: Callable[..., Any],
        setter: Callable[[...], None],
) -> Callable[..., None]:
    """

    :param obj:
    :param pname:
    :param ptype:
    :param duration:
    :param vrange:
    :param getter:
    :param setter:
    :return:
    """
    @asyncSlot()
    async def animate() -> None:
        obj.animation = QPropertyAnimation(obj, pname.encode())
        obj.animation.setDuration(int(duration * 1000))
        obj.animation.setStartValue(vrange[0])
        obj.animation.setEndValue(vrange[1])
        obj.animation.start()

    setattr(obj, pname, Property(ptype, getter, setter))
    return lambda: obj.emit_event(animate)
