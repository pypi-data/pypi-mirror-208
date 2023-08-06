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

"""
Implementation of queue of messages received from a RabbitMQ stream.
"""

import asyncio
from collections import deque

from libc.stdint cimport int32_t, uint16_t

from ..amqp import MessageCtx

cdef class MessageQueue:
    """
    RabbitMQ stream message queue.

    The queue allows to coordinate receiving of messages from a RabbitMQ
    stream, and enables control of RabbitMQ stream subscription credit.
    """
    cdef:
        uint16_t _initial_credit
        int32_t _credit
        uint16_t _maxsize
        object _loop
        object _task

        public object data

    def __cinit__(self, _initial_credit: int, maxsize: int):
        """
        Initialize message queue.

        :param _initial_credit: Initial value of RabbitMQ stream
            subscription credit.
        :param maxsize: Size of queue determining if RabbitMQ
            stream subscription credit can be renewed.
        """
        self._credit = self._initial_credit = _initial_credit
        self._maxsize = maxsize

        self.data = deque([])

        self._loop = asyncio.get_event_loop()
        self._task = self._loop.create_future()

    cpdef put(self, message: MessageCtx):
        """
        Add message into the queue.
        """
        self.data.append(message)

    def set(self) -> bool:
        """
        Mark queue as populated with messages from RabbitMQ stream.

        Any coroutine waiting with :py:meth:`MessageQueue.wait` is woken
        up.

        Return true if RabbitMQ stream subscription credit needs to be
        renewed.
        """
        # message has been just received, therefore credit > 0
        assert self._credit > 0
        self._credit -= 1
        if not self._task.done():
            self._task.set_result(None)

        return self._credit <= self._initial_credit \
            and len(self.data) < self._maxsize

    async def wait(self) -> None:
        """
        Wait for the queue to be populated with messages from RabbitMQ
        stream.
        """
        task = self._task
        if task.done() and self.data:
            return
        elif task.done():
            task = self._task = self._loop.create_future()
        await task

    def empty(self) -> bool:
        """
        Check if subscription credit needs to be renewed.
        """
        assert self._credit >= 0
        return self._credit < self._initial_credit and len(self.data) == 0

    def inc_credit(self) -> int:
        """
        Increase credit value.

        Credit is set to initial credit value. Therefore, the credit is
        increased by difference between initial credit value and old credit
        value. The difference is returned.

        Note, that it only changes `_credit` attribute. Subscription credit
        needs to be renewed via RabbitMQ Streams protocol as well.

        .. seealso:: :py:meth:`rbfly.streams.protocol.RabbitMQStreamsProtocol`
        """
        assert self._credit < self._initial_credit
        delta = self._initial_credit - self._credit
        self._credit += delta
        return delta

    @property
    def task(self):
        return self._task

# vim: sw=4:et:ai
