# Copyright (C) 2022 Bjarne von Horn (vh at igh dot de).
#
# This file is part of the PdCom library.
#
# The PdCom library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# The PdCom library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more .
#
# You should have received a copy of the GNU Lesser General Public License
# along with the PdCom library. If not, see <http://www.gnu.org/licenses/>.


from asyncio import CancelledError, Task, get_event_loop, wait
from typing import Awaitable, Callable, Iterable

try:
    from typing import Protocol
except ImportError:

    class Protocol:
        pass


class WatchTask(Protocol):
    async def wait_for_error(self) -> None:
        pass

    async def good(self) -> bool:
        return True


async def task_impl(task, callback):
    while True:
        try:
            await task.wait_for_error()
        except CancelledError:
            raise
        else:
            await callback()


class Watchdog:
    """Watchdog to monitor states etc.

    Remeber to stop() the watchdog to stop its monitoring tasks.
    You can also use it as a context manager:
    .. highlight:: python
    .. code-block:: python

        async with Watchdog(callback, tasks) as watchdog:
            await work()

    :param callback: Nofitication when an error occured
    :param tasks: Iterable of tasks, which should implement all WatchTask properties.
    """

    def __init__(
        self, callback: Callable[[], Awaitable[None]], tasks: "Iterable[WatchTask]"
    ):
        self._watch_tasks = set(tasks)
        self._wait_error_tasks: set[Task] = set()
        self._callback = callback

    async def __aenter__(self):
        self.start()

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()
        return False

    def start(self):
        loop = get_event_loop()
        for task in self._watch_tasks:
            self._wait_error_tasks.add(
                loop.create_task(task_impl(task, self._callback))
            )

    async def stop(self):
        tasks = self._wait_error_tasks
        self._wait_error_tasks = set()
        for task in tasks:
            if not task.done():
                task.cancel()
        await wait(tasks)
        # gather all exceptions and raise one which is not CancelledError
        # all other exceptions will be dropped
        ex_to_raise = None
        for task in tasks:
            ex = task.exception()
            if not isinstance(ex, CancelledError) and ex_to_raise is None:
                ex_to_raise = ex
        if ex_to_raise is not None:
            raise ex_to_raise
