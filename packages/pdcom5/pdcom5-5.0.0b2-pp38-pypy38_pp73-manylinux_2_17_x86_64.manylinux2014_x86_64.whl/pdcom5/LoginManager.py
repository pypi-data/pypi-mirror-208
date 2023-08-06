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

from asyncio import Future, get_event_loop
from . import _PdComWrapper as PdComWrapper


class LoginManager(PdComWrapper.SimpleLoginManager):
    def __init__(self, hostname: str, username, password):
        super().__init__(hostname)
        self._username = username
        self._password = password
        self._future: Future = get_event_loop().create_future()

    def getAuthname(self) -> str:
        ans = self._username
        self._username = ""
        return ans

    def getPassword(self) -> str:
        ans = self._password
        self._password = ""
        return ans

    def completed(self, success: PdComWrapper.SimpleLoginManager.LoginResult) -> None:
        if self._future is not None and not self._future.cancelled():
            self._future.set_result(success)
        self._future = None

    async def login(self) -> bool:
        if self._future is not None:
            return (
                await self._future
            ) == PdComWrapper.SimpleLoginManager.LoginResult.Success
        fut = get_event_loop().create_future()
        self._future = fut
        if not PdComWrapper.SimpleLoginManager.login(self):
            fut.cancel()
            return False
        return (await fut) == PdComWrapper.SimpleLoginManager.LoginResult.Success

    async def logout(self):
        PdComWrapper.SimpleLoginManager.logout(self)
