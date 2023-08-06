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

from asyncio import FIRST_COMPLETED, Future, get_event_loop, wait, wait_for
from . import _PdComWrapper as PdComWrapper
from .Variable import Variable
from datetime import timedelta
from numbers import Number
from typing import Any, Callable, Optional, Union
from weakref import WeakSet
import numpy


class _Subscription(PdComWrapper.Subscription):
    def __init__(
        self,
        subscriber: "SubscriberBase",
        variable: Union[str, PdComWrapper.Variable],
        fut: Future,
        selector: Optional[PdComWrapper.Selector],
    ):
        if isinstance(variable, str):
            super().__init__(
                subscriber._subscriber,
                subscriber._subscriber._process._process,
                variable,
                selector,
            )
        else:
            super().__init__(subscriber._subscriber, variable._v, selector)
        self._pending_subscription_future = fut


class Subscription:
    State = PdComWrapper.Subscription.State
    """State enum of a subscription"""

    def __init__(
        self,
        subscriber: "SubscriberBase",
        variable: Union[str, PdComWrapper.Variable],
        fut: Future,
        selector: Optional[PdComWrapper.Selector],
    ):
        self.subscriber = subscriber
        self._subscription = _Subscription(subscriber, variable, fut, selector)
        subscriber._subscriber._subscriptions.add(self)
        # trigger process to call callbacks in case subscription is already ready
        subscriber._subscriber._process._process.callPendingCallbacks()

    def cancel(self):
        """Cancel a subscription."""
        if self._subscription is not None:
            self._subscription.cancel()
            self._subscription = None

    async def poll(self):
        """Poll an existing subscription.

        This can for example be used to refresh an event-based subscription.
        """
        # FIXME(vh) in case of event or periodic subscription,
        # newValues() may be called prematurely
        self._subscription.poll()
        await self.subscriber.newValues()
        return self.value

    async def read(self):
        """Wait for an update and return the new value.

        :return: tuple of (value, timestamp)
        """
        ts = await self.subscriber.newValues()
        return (self.value, ts)

    @property
    def value(self):
        """The current value."""
        v = self._subscription.value
        if v.shape == (1,):
            return v[0]
        else:
            return v

    @property
    def variable(self):
        """The corresponding variable."""
        return Variable(self._subscription.variable)

    @property
    def state(self) -> "Subscription.State":
        """The current state of the subscription."""
        return self._subscription.state

    async def waitUntilValueEquals(self, desired_value, timeout=None):
        """Block until Variable Value equals desired value.

        :param desired_value: Desired value.
        :param timeout: Optional Timeout in seconds
        """
        await self.waitForValueToBe(lambda x: x == desired_value, timeout)

    async def waitForValueToBe(self, predicate: Callable[[Any], bool], timeout=None):
        """Block until predicate called with Variable Value evaluates to true.

        :param predicate: Callback with value as argument.
        :param timeout: Optional Timeout in seconds
        """
        waiting = True
        while waiting:
            await wait_for(self.subscriber.newValues(), timeout)
            if predicate(self.value):
                waiting = False

    def __iter__(self):
        """Iterate Row-wise over values."""
        return numpy.nditer(self._subscription.value, order="C")


class _Subscriber(PdComWrapper.Subscriber):
    def __init__(self, process, transmission: PdComWrapper.Transmission):
        if isinstance(transmission, timedelta):
            transmission = PdComWrapper.Transmission(transmission)
        elif isinstance(transmission, Number):
            transmission = PdComWrapper.Transmission(timedelta(seconds=transmission))
        super().__init__(transmission)
        self._process = process
        process._process._subscribers.add(self)
        self._newvalues_futures: set[Future] = set()
        self._subscriptions = WeakSet()

    def stateChanged(self, s: PdComWrapper.Subscription) -> None:
        if s.state == s.State.Active and s._pending_subscription_future is not None:
            if not s._pending_subscription_future.cancelled():
                s._pending_subscription_future.set_result(None)
            s._pending_subscription_future = None
        elif s.state == s.State.Invalid and s._pending_subscription_future is not None:
            if not s._pending_subscription_future.cancelled():
                s._pending_subscription_future.set_exception(
                    PdComWrapper.InvalidSubscription()
                )
            s._pending_subscription_future = None

    def newValues(self, time: timedelta) -> None:
        futures = self._newvalues_futures
        self._newvalues_futures = set()
        for fut in futures:
            if not fut.cancelled():
                fut.set_result(time)


class SubscriberBase:
    def __init__(self, process, transmission: PdComWrapper.Transmission):
        self._subscriber = _Subscriber(process, transmission)

    async def newValues(self) -> timedelta:
        """New Values arrived callback.

        This is a coroutine, so you have to ``await`` it.
        :return: Timestamp when the data has been sent.
        """
        fut = get_event_loop().create_future()
        self._subscriber._newvalues_futures.add(fut)
        return await fut


class Subscriber(SubscriberBase):
    """Variable subscriber.

    This class manages how variables are subscribed and the callback when new
    values are received.

    :param process: Process instance
    :param transmission: Kind of subscription (poll, event based, periodic)
    """

    def __init__(self, process, transmission: PdComWrapper.Transmission):
        super().__init__(process, transmission)

    async def subscribe(
        self,
        variable: Union[str, PdComWrapper.Variable],
        selector: Optional[PdComWrapper.Selector] = None,
    ) -> Subscription:
        """Subscribe to a variable.

        :param variable: Variable to subscribe.
        :param selector: Optional selector to create a view on multidimensional data.

        :return: a Subscription instance.
        """
        fut = get_event_loop().create_future()
        ans = Subscription(self, variable, fut, selector)
        await fut
        return ans

    async def waitUntilAllValuesEqual(
        self,
        kv: "dict[Union[str, Subscription], Any]",
        timeout=None,
    ):
        """Synchronize signals.

        Blocks until all variables are equal to the desired values.
        :param kv: dict of variables and the corresponding desired values.
        :param timeout: Timeout in seconds, default infinite.
        """

        def predicate_factory(v):
            return lambda x: x == v

        pred_map = {k: predicate_factory(v) for k, v in kv.items()}
        await self.waitForValuesToBe(pred_map, timeout)

    async def waitUntilAllValuesGreaterEqual(
        self,
        kv: "dict[Union[str, Subscription], Any]",
        timeout=None,
    ):
        """Synchronize signals.

        Blocks until all variables are greater than or equal to the desired values.
        :param kv: dict of variables and the corresponding desired values.
        :param timeout: Timeout in seconds, default infinite.
        """

        def predicate_factory(v):
            return lambda x: x >= v

        pred_map = {k: predicate_factory(v) for k, v in kv.items()}
        await self.waitForValuesToBe(pred_map, timeout)

    async def waitForValuesToBe(
        self,
        kv: "dict[Union[str, Subscription], Callable[[Any], bool]]",
        timeout=None,
    ):
        """Synchronize signals.

        Blocks until all predicates evaluate to true.
        :param kv: dict of variables and the corresponding predicates.
        :param timeout: Timeout in seconds, default infinite.
        """
        pending = set()
        subscriptions = []
        loop = get_event_loop()
        try:
            for _sub, predicate in kv.items():
                if not isinstance(_sub, Subscription):
                    sub = await self.subscribe(_sub)
                else:
                    sub = _sub
                subscriptions.append(sub)
                pending.add(loop.create_task(sub.waitForValueToBe(predicate)))

            while len(pending) > 0:
                (done, pending) = await wait(
                    pending, timeout=timeout, return_when=FIRST_COMPLETED
                )
                for p in pending:
                    p.cancel()
                if len(done) == 0:
                    raise TimeoutError("Timeout waiting for all values")
                # allow propagating a possible exception
                exception = None
                for task in done:
                    if task.cancelled():
                        continue
                    tmp_ex = task.exception()
                    if exception is None:
                        exception = tmp_ex
                if exception is not None:
                    raise exception
        finally:
            for p in pending:
                if not p.done():
                    p.cancel()
            if len(pending) > 0:
                (done, _) = await wait(pending)
                for d in done:
                    d.exception()
