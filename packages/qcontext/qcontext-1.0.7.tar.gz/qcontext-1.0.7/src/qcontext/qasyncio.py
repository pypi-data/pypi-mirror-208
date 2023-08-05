import functools
import asyncio
import qasync
import sys
from qasync import asyncSlot  # to import `asyncSlot` from `qasyncio`


class AsyncApp:
    __future = None

    async def __aenter__(self):
        def close_future(future, loop):
            loop.call_later(10, future.cancel)
            future.cancel()

        loop = asyncio.get_event_loop()
        future = asyncio.Future()

        qapp = qasync.QApplication.instance()
        if hasattr(qapp, 'aboutToQuit'):
            getattr(qapp, 'aboutToQuit').connect(functools.partial(close_future, future, loop))
        self.__future = future

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.__future

    @staticmethod
    def run(run_app):
        try:
            qasync.run(run_app())
        except asyncio.exceptions.CancelledError:
            sys.exit(0)
