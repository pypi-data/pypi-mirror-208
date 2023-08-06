from typing import Callable, Awaitable
import functools
import asyncio
import qasync
import sys
from qasync import asyncSlot  # to import `asyncSlot` from `qasyncio`


class AsyncApp:
    @staticmethod
    def run(amain: Callable[[], Awaitable[None]]) -> None:
        async def wrap():
            def close_future(future: asyncio.Future, loop: asyncio.AbstractEventLoop) -> None:
                loop.call_later(10, future.cancel)
                future.cancel()
            future = asyncio.Future()
            if hasattr(qapp := qasync.QApplication.instance(), 'aboutToQuit'):
                getattr(qapp, 'aboutToQuit').connect(functools.partial(close_future, future, asyncio.get_event_loop()))
            await amain()
            await future

        try:
            qasync.run(wrap())
        except asyncio.exceptions.CancelledError:
            sys.exit(0)


# def to_async_slot(to_call):
#     @asyncSlot()
#     async def wrapped():
#         print(type(to_call))
#         if to_call.__class__.__name__ in ('function', 'method'):
#             await to_call()
#         # elif
#     return wrapped
