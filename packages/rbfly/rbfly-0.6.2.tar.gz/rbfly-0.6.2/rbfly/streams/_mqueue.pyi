#
# rbfly - a library for RabbitMQ Streams using Python asyncio
#
# Copyright (C) 2021-2023 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import asyncio
from collections import deque

from ..amqp import MessageCtx

class MessageQueue:
    task: asyncio.Future[None]

    default_credit: int
    data: deque[MessageCtx]

    def __init__(self, default_credit: int, queue_threshold: int) -> None: ...
    def put(self, message: MessageCtx) -> None: ...
    def set(self) -> bool: ...
    def empty(self) -> bool: ...
    async def wait(self) -> None: ...

    def inc_credit(self) -> int: ...

# vim: sw=4:et:ai
