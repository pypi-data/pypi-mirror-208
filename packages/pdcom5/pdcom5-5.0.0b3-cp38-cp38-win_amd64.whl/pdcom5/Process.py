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

from . import _PdComWrapper as PdComWrapper
from ._PdComWrapper import Message
from .Subscription import Subscriber, Subscription, _Subscriber, SubscriberBase
from .Variable import Variable
from asyncio import get_event_loop, wait_for, Future, Protocol, Transport
from datetime import timedelta
from ssl import SSLContext, create_default_context
from typing import Optional, Union
from urllib.parse import urlparse, unquote
from weakref import WeakSet


class ListReply:
    """Reply of Process.list()."""

    def __init__(self, vars, dicts):
        self.variables = [Variable(v) for v in vars]
        """List of Variables."""
        self.directories = dicts
        """List of directories."""


class BroadcastMessage:
    """Broadcast Message."""

    def __init__(self, msg, attr, time, user):
        self.message = msg
        self.attribute_name = attr
        self.time = time
        self.user = user


class LoginFailed(RuntimeError):
    """Login has failed (e.g. invalid password etc.)"""

    pass


class _Process(Protocol, PdComWrapper.Process, PdComWrapper.MessageManagerBase):
    def __init__(self, appname, loginManager):
        Protocol.__init__(self)
        PdComWrapper.Process.__init__(self)
        PdComWrapper.MessageManagerBase.__init__(self)
        self._transport: Transport = None
        self._buf = bytearray()
        self._clear_futures()
        self._appname = appname
        self._login_manager = loginManager
        if loginManager is not None:
            self.setAuthManager(loginManager)
        self.setMessageManager(self)

    def _clear_futures(self):
        self._connected_queue: list[Future] = [get_event_loop().create_future()]
        self._initial_connected_future = self._connected_queue[0]
        self._find_queue: list[Future] = []
        self._list_queue: list[Future] = []
        self._ping_queue: list[Future] = []
        self._get_message_queue: list[Future] = []
        self._get_active_messages_queue: list[Future] = []
        self._get_client_statistics_queue: list[Future] = []
        self._broadcast_set: set[Future] = set()
        self._process_message_set: set[Future] = set()
        self._subscribers: WeakSet[_Subscriber] = WeakSet()

    def _cancel_all_futues(self, exc):
        futs = self._find_queue
        futs += self._connected_queue
        futs += self._list_queue
        futs += self._ping_queue
        futs += self._get_message_queue
        futs += self._get_active_messages_queue
        futs += self._get_client_statistics_queue
        for f in futs:
            if not f.cancelled():
                f.set_exception(exc)
        for f in self._broadcast_set:
            if not f.cancelled():
                f.set_exception(exc)
        for f in self._process_message_set:
            if not f.cancelled():
                f.set_exception(exc)
        for s in self._subscribers:
            for f in s._newvalues_futures:
                if not f.cancelled():
                    f.set_exception(exc)
            s._newvalues_futures = set()
            for _sub in s._subscriptions:
                sub = _sub._subscription
                if sub._pending_subscription_future is not None:
                    if not sub._pending_subscription_future.cancelled():
                        sub._pending_subscription_future.set_exception(exc)
                    sub._pending_subscription_future = None
            s._subscriptions = WeakSet()

        self._clear_futures()
        self.reset()

    def connection_made(self, transport: Transport):
        self._transport = transport

    def eof_received(self):
        pass

    def connection_lost(self, exc):
        if exc is None:
            exc = EOFError()
        self._cancel_all_futues(exc)

    def write(self, b: memoryview) -> None:
        self._transport.write(b)

    def data_received(self, data):
        self._buf += data
        while len(self._buf) > 0:
            self.asyncData()

    def read(self, b: memoryview) -> int:
        count = min(len(b), len(self._buf))
        b[:count] = self._buf[:count]
        self._buf[:] = self._buf[count:]
        return count

    def applicationName(self) -> str:
        return str(self._appname)

    def connected(self) -> None:
        if len(self._connected_queue) > 0:
            f = self._connected_queue.pop(0)
            if not f.cancelled():
                f.set_result(None)

    def listReply(self, vars: list, directiores: list) -> None:
        if len(self._list_queue) > 0:
            fut = self._list_queue.pop(0)
            if not fut.cancelled():
                fut.set_result(ListReply(vars, directiores))

    def findReply(self, var: Optional[PdComWrapper.Variable]) -> None:
        if len(self._find_queue) > 0:
            fut = self._find_queue.pop(0)
            if fut.cancelled():
                return
            if var is None:
                fut.set_result(var)
            else:
                fut.set_result(Variable(var))

    def clientStatisticsReply(
        self, statistics: "list[PdComWrapper.ClientStatistics]"
    ) -> None:
        if len(self._get_client_statistics_queue) > 0:
            fut = self._get_client_statistics_queue.pop(0)
            if fut.cancelled():
                return
            fut.set_result(statistics)

    def pingReply(self) -> None:
        if len(self._ping_queue) > 0:
            fut = self._ping_queue.pop(0)
            if not fut.cancelled():
                fut.set_result(None)

    #    def alive(self) -> None:
    #        pass

    def broadcastReply(
        self, message: str, attr: str, time: timedelta, user: str
    ) -> None:
        all_fut = self._broadcast_set
        self._broadcast_set = set()
        for fut in all_fut:
            if not fut.cancelled():
                fut.set_result(BroadcastMessage(message, attr, time, user))

    def processMessage(self, message: Message) -> None:
        future_set = self._process_message_set
        self._process_message_set = set()
        for fut in future_set:
            if not fut.cancelled():
                fut.set_result(message)

    def getMessageReply(self, message: Message) -> None:
        if len(self._get_message_queue) == 0:
            return
        fut = self._get_message_queue.pop(0)
        if not fut.cancelled():
            fut.set_result(message)

    def activeMessagesReply(self, messages: "list[Message]") -> None:
        if len(self._get_active_messages_queue) == 0:
            return
        fut = self._get_active_messages_queue.pop(0)
        if not fut.cancelled():
            fut.set_result(messages)


class Process:
    """PdCom Process.

    :param appname: Name of this application, default "".
    """

    def __init__(self, appname: str = ""):
        self._process = None
        self._appname = appname
        self._server_name = ""

    async def ping(self, timeout: float = None):
        """ping the server."""
        fut = get_event_loop().create_future()
        self._process._ping_queue.append(fut)
        self._process.ping()
        await wait_for(fut, timeout)

    async def connect(self, url: str, ssl_ctx: Optional[SSLContext] = None):
        """Create a connection.

        :param url: URL of the server, format msr[s]://user:password@server.port
        :param ssl_ctx: Optional SSLContext instance for secure communication.

        :raise LoginFailed: Login has failed
        :raise LoginRequired: Login is required by the server but no credentials were supplied.
        """
        loop = get_event_loop()
        url = urlparse(url)
        port = url.port
        self._server_name = url.hostname
        if url.scheme == "msr":
            if port is None:
                port = 2345
        elif url.scheme == "msrs" or ssl_ctx is not None:
            if url.port is None:
                port = 4523
        if url.scheme == "msrs" and ssl_ctx is None:
            ssl_ctx = create_default_context()

        lm = None
        if url.username is not None:
            if not PdComWrapper.has_sasl():
                raise ValueError("PdCom built without SASL support")
            from .LoginManager import LoginManager

            lm = LoginManager(
                url.hostname, unquote(url.username), unquote(url.password)
            )

        def process_factory():
            return _Process(self._appname, lm)

        (t, p) = await loop.create_connection(
            process_factory, url.hostname, port, ssl=ssl_ctx
        )
        self._process = p
        try:
            if lm is not None:
                if not await lm.login():
                    raise LoginFailed("Login has failed")

            await self._process._initial_connected_future

        finally:
            if self._process._initial_connected_future.done():
                self._process._initial_connected_future.exception()
            else:
                self._process._initial_connected_future.cancel()
            self._process._initial_connected_future = None

    def close(self):
        """Close the connection."""
        if self._process is not None:
            self._process._transport.close()
            self._process = None

    async def find(self, path: str) -> Optional[Variable]:
        """Find a Variable.

        :return: None (if Variable not found) or Variable
        """
        fut = get_event_loop().create_future()
        self._process._find_queue.append(fut)
        self._process.find(path)
        return await fut

    async def list(self, path: str = "") -> ListReply:
        """List all Variables and directories."""
        fut = get_event_loop().create_future()
        self._process._list_queue.append(fut)
        self._process.list(path)
        return await fut

    async def getClientStatistics(self) -> "list[PdComWrapper.ClientStatistics]":
        """Get statistics about all connected clients."""
        fut = get_event_loop().create_future()
        self._process._get_client_statistics_queue.append(fut)
        self._process.getClientStatistics()
        return await fut

    def create_subscriber(self, transmission: PdComWrapper.Transmission) -> Subscriber:
        """Create a Subscriber instance."""
        return Subscriber(self, transmission)

    async def subscribe(
        self,
        transmission: PdComWrapper.Transmission,
        variable: Union[str, PdComWrapper.Variable],
        selector: Optional[PdComWrapper.Selector] = None,
    ) -> Subscription:
        """Subscribe to a Variable.

        :param transmission: Transmission mode, can also be a float (=period in seconds)
                             or timedelta instance.
        :param variable: The Variable to subscribe to, or its path.
        :param selector: Optional selector to create a view on multidimensional data.
        """
        fut = get_event_loop().create_future()
        subscriber = SubscriberBase(self, transmission)
        ans = Subscription(subscriber, variable, fut, selector)
        await fut
        return ans

    async def setVariableValue(self, var: Union[Variable, str], value):
        """Set a variable to a given value.

        :param var: Variable or its path.
        :param value: Desired value.
        """
        if not isinstance(var, Variable):
            var = await self.find(var)
        if var is None:
            raise ValueError("Variable not found")
        await var.setValue(value)

    async def getVariableValue(self, var: Union[Variable, str]):
        """Get the current value of a variable.

        :param var: Variable or its path.
        """
        if not isinstance(var, Variable):
            var = await self.find(var)
            if var is None:
                raise ValueError("Variable not found")
        return await var.poll()

    async def pollMessage(self) -> Message:
        """Wait for a new Event to happen/for a message to be sent."""
        fut = get_event_loop().create_future()
        self._process._process_message_set.add(fut)
        return await fut

    async def getMessage(self, id: int) -> Optional[Message]:
        """Get a specific message.

        :param id: Number of the Message.
        """
        fut = get_event_loop().create_future()
        self._process._get_message_queue.append(fut)
        self._process.getMessage(id)
        ans: Message = await fut
        if len(ans.path) == 0:
            return None
        return ans

    async def activeMessages(self) -> "list[Message]":
        """Get a list of active messages.

        Active messages are messages which haven't been resetted yet.
        """
        fut = get_event_loop().create_future()
        self._process._get_active_messages_queue.append(fut)
        self._process.activeMessages()
        return await fut

    @property
    def name(self) -> str:
        """Name of the server application."""
        return self._process.name

    @property
    def version(self) -> str:
        """Version of the server application"""
        return self._process.version

    async def broadcast(self, message: str, attr: str = "text"):
        """Send a broadcast message to all clients.

        :param message: Message
        :param attr: type of the message, default 'text'
        """
        self._process.broadcast(message, attr)

    async def pollBroadcast(self) -> BroadcastMessage:
        fut = get_event_loop().create_future()
        self._process._broadcast_set.add(fut)
        return await fut

    async def login(self, user, password):
        if not PdComWrapper.has_sasl():
            raise ValueError("PdCom built without SASL support")
        from .LoginManager import LoginManager

        lm = LoginManager(self._server_name, user, password)

        self._process._login_manager = lm

        if not await lm.login():
            raise LoginFailed()

    async def logout(self):
        if self._process._login_manager is not None:
            await self._process._login_manager.logout()
