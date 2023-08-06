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


from datetime import timedelta
from . import _PdComWrapper as PdComWrapper
from asyncio import get_event_loop
from numbers import Number
from typing import Optional, Union
import numpy as np
from warnings import warn


class TemporaryValueChange:
    """Helper to change a variable temporarily at block scope.

    Example:

    .. highlight:: python
    .. code-block:: python

        async with TemporaryValueChange(variable, 5.0, 1.0):
            # variable is now 5.0
            # do now some work
        # scope is left, variable is now 1.0
    """

    def __init__(
        self,
        var: "Variable",
        new_value: Union[np.ndarray, Number],
        old_value: Union[np.ndarray, Number],
    ):
        """Ctor.

        :param var: Variable
        :param new_value: Value to be set at begin of block scope
        :param old_value: Value to be set at the end of block scope
        """
        self._variable = var
        self._new_value = new_value
        self._old_value = old_value

    async def __aenter__(self):
        await self._variable.setValue(self._new_value)

    async def __aexit__(self, exc_type, exc, tb):
        await self._variable.setValue(self._old_value)
        # we can't handle any exceptions
        return False


class Variable:
    """Process Variable, can be retrieved via Process.find()."""

    def __init__(self, v: PdComWrapper.Variable):
        self._v = v

    async def setValue(
        self,
        value: Union[np.ndarray, Number],
        selector: Optional[PdComWrapper.Selector] = None,
    ):
        """Set the given variable to a certain value.

        This is a coroutine, so you have to await it.

        :param value: the desired value
        :param selector: Optional selector to change a subset of a multidimensional variable.
        """
        if isinstance(value, (Number, bool)):
            value = np.array((value,))
        elif not isinstance(value, np.ndarray):
            value = np.array(value)
        cpp_future = self._v.setValue(value, selector)
        if cpp_future.empty:
            warn("Server does not support parameter write feedback")
            return
        fut = get_event_loop().create_future()
        fut._pdcom_cpp_future = cpp_future

        def resolve():
            if not fut.cancelled():
                fut.set_result(None)

        def reject(ex):
            if not fut.cancelled():
                fut.set_exception(ex)

        cpp_future.then(resolve)
        cpp_future.handle_exception(reject)
        await fut

    def temporaryTrue(self):
        """Set a bool parameter to True temporarily.

        Use this in an ``async with`` statement:

        .. highlight:: python
        .. code-block:: python

            async with variable.temporaryTrue():
                # variable is now True until the block scope is left
                pass
        """
        return TemporaryValueChange(self, True, False)

    def temporaryFalse(self):
        return TemporaryValueChange(self, False, True)

    @property
    def empty(self) -> bool:
        """Whether the variable handle is empty (usually not the case)"""
        return self._v.empty

    @property
    def path(self) -> str:
        """Path of the variable"""
        return self._v.path

    @property
    def name(self) -> str:
        """Name of the variable (last part of the path)"""
        return self._v.name

    @property
    def shape(self):
        """Shape of the variable"""
        return tuple(self._v.shape)

    async def poll(self) -> "tuple[Union[Number, np.ndarray], timedelta]":
        """Poll a Variable without a subscription."""
        fut = get_event_loop().create_future()
        cpp_future = self._v.poll()
        fut._pdcom_cpp_future = cpp_future

        def resolve(result, timestamp):
            result = result.value
            if result.shape == (1,):
                result = result[0]
            if not fut.cancelled():
                fut.set_result((result, timestamp))

        def reject(ex):
            if not fut.cancelled():
                # workaround: c++ exceptions registered by pybind11 can't be
                # normal python classes, so they have to be exported twice
                if isinstance(ex, PdComWrapper.ProcessGoneAwayClass):
                    ex = PdComWrapper.ProcessGoneAway()
                fut.set_exception(ex)

        cpp_future.then(resolve)
        cpp_future.handle_exception(reject)
        return await fut
