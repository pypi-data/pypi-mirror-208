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
RabbitMQ Streams publishers (producers) and subscribers (consumers).

Publishers sending messages in AMQP format for two scenarios are implemented

- sending single message
- sending batch of messages

There are also publishers for sending opaque binary data implemented. These
are used to measure overhead of AMQP 1.0 encoding with the official
publishers. While these are not part of official API, they still can be
used and are supported.

Subscriber class implements RabbitMQ Streams message consumer. It supports
both AMQP 1.0 message format and opaque binary data.
"""

import asyncio
import cython
import logging
import typing as tp
from collections import deque

from ..amqp._message cimport MessageCtx
from ..types import AMQPBody
from .offset import Offset

from libc.stdint cimport uint64_t

logger = logging.getLogger(__name__)

class PublisherConstr(tp.Protocol):
    """
    Interface for publisher classes constructor.
    """
    def __init__(self, client, stream, id, name, message_id):
        ...

cdef class PublisherTrait:
    """
    Trait with basic publisher funcionality.

    :var client: RabbitMQ Streams client.
    :var stream: RabbitMQ stream name.
    :var id: Publisher id.
    :var name: Publisher reference name.
    :var message_id: Last value of published message id.
    """
    cdef:
        public int id
        public str name
        public str stream
        public uint64_t message_id
        object client
        object _lock
    def __cinit__(
            self,
            object client, str stream, int id, str name, uint64_t message_id
    ):
        """
        Create publisher.

        :param client: RabbitMQ Streams client.
        :param stream: RabbitMQ stream name.
        :param id: Publisher id.
        :param name: Publisher reference name.
        :param message_id: Last value of published message id.
        """
        self.client = client
        self.stream = stream
        self.id = id
        self.name = name
        self.message_id = message_id
        self._lock = asyncio.Lock()

    cpdef uint64_t next_message_id(self, uint64_t inc=1):
        """
        Get next value of message id.

        :param inc: Value by which to increase the message id.
        """
        self.message_id += inc
        return self.message_id

    async def _publish(self, message_id: uint64_t, *data: MessageCtx | bytes, amqp: bool=True) -> None:
        """
        Publish multiple messages to RabbitMQ stream.

        Connection error is ignored and then sending of messages is
        retried.

        :param message_id: Starting message id of published messages.
        :param data: Collection of messages to publish.
        :param amqp: Send messages in AMQP format or just opaque data.
        """
        count = 0
        while True:
            protocol = await self.client.get_protocol()
            try:
                async with self._lock:
                    count = await protocol.publish(
                        self.id, self.message_id, *data, amqp=amqp
                    )
            except ConnectionError:
                if __debug__:
                    logger.debug('Connection error when publishing messages')
                pass
            else:
                break
        return count

cdef class PublisherBatchTrait:
    """
    RabbitMQ Streams publisher trait for sending messages in batches.
    """
    def __init__(
            self,
            client,
            stream: str,
            id: cython.int,
            name: str,
            message_id: uint64_t
        ):
        """
        Create batch publisher for sending messages in AMQP format.
        """
        self._data: cython.list = []

cdef class Publisher(PublisherTrait):
    """
    RabbitMQ Streams publisher for sending single message in AMQP format.

    .. seealso::

       - :py:class:`rbfly.streams.PublisherBatchMem`
       - :py:class:`rbfly.streams.PublisherBatch`
    """
    async def send(self, body: AMQPBody) -> None:
        """
        Send AMQP message to RabbitMQ stream.

        :param body: AMQP message body.
        """
        msg = MessageCtx(body)
        await self._publish(self.message_id, msg)
        self.next_message_id()

class PublisherBatch(PublisherTrait, PublisherBatchTrait):
    """
    RabbitMQ Streams publisher for sending batch of messages in
    AMQP format.

       - :py:class:`rbfly.streams.PublisherBatchMem`
       - :py:class:`rbfly.streams.Publisher`
    """
    def batch(self, body: AMQPBody) -> None:
        """
        Enqueue single message for batch processing.

        There is no protection against number of messages, which can be
        batched. Therefore, if flushing of messages is not performed on
        regular basis, an application using this publisher can run out of
        memory.

        :param body: Body of AMQP message.

        .. seealso:: :py:meth:`.PublisherBatch.flush`
        """
        self._data.append(body)

    async def flush(self) -> None:
        """
        Flush all enqueued messages.

        .. seealso:: :py:meth:`.PublisherBatch.batch`
        """
        while self._data:
            data = (MessageCtx(v) for v in self._data)
            count = await self._publish(self.message_id, *data)

            self.next_message_id(count)
            del self._data[:count]

class PublisherBatchMem(PublisherTrait, PublisherBatchTrait):
    """
    RabbitMQ Streams publisher for sending batch of messages in
    AMQP format with memory protection.

    ... seealso::

       - :py:class:`rbfly.streams.PublisherBatch`
       - :py:class:`rbfly.streams.Publisher`
    """
    def __init__(
            self,
            client,
            stream: str,
            id: cython.int,
            name: str,
            message_id: uint64_t
        ):
        """
        Create batch publisher for sending messages in AMQP format.
        """
        super().__init__(client, stream, id, name, message_id)
        self._cond: asyncio.Condition = asyncio.Condition()

    async def batch(self, body: AMQPBody, *, max_len: int) -> None:
        """
        Enqueue single message for batch processing.

        Method blocks if `max_len` messages are enqueued. To unblock, call
        :py:meth:`.PublisherBatchMem.flush` method.

        :param body: Body of AMQP message.

        .. seealso:: :py:meth:`.PublisherBatchMem.flush`
        """
        cond = self._cond
        async with cond:
            await cond.wait_for(lambda: len(self._data) < max_len)
            self._data.append(body)

    async def flush(self) -> None:
        """
        Flush all enqueued messages and unblock
        :py:meth:`.PublisherBatch.batch` calls.

        .. seealso:: :py:meth:`.PublisherBatchMem.batch`
        """
        if not self._data:
            return

        cond = self._cond
        async with cond:
            data = (MessageCtx(v) for v in self._data)
            await self._publish(self.message_id, *data)

            self.next_message_id(len(self._data))
            self._data.clear()

            cond.notify_all()

#
# purely binary publishers; application is reponsible for data encoding and
# decoding; their implementation is for performance comparision purposes
# only
#

cdef class PublisherBin(PublisherTrait):
    """
    RabbitMQ Streams publisher for sending single message of binary data.

    An application is responsible for encoding and decoding the format of
    the data.

    .. seealso:: `Publisher`
    """
    async def send(self, message: bytes) -> None:
        """
        Send message binary data to RabbitMQ stream.

        :param message: Message binary data.
        """
        await self._publish(self.message_id, message, amqp=False)
        self.next_message_id()

class PublisherBinBatch(PublisherTrait, PublisherBatchTrait):
    """
    RabbitMQ Streams publisher for sending batch of messages in
    application's binary format.

    An application is responsible for encoding and decoding the format of
    the data.

    .. seealso:: `Publisher`
    """
    def batch(self, message: bytes) -> None:
        """
        Enqueue single message for batch processing.

        :param message: Binary message to send.

        .. seealso:: :py:meth:`.PublisherBinBatch.flush`
        """
        self._data.append(message)

    async def flush(self) -> None:
        """
        Flush all enqueued messages.

        .. seealso:: `batch`
        """
        await self._publish(self.message_id, *self._data, amqp=False)
        self.next_message_id(len(self._data))
        self._data.clear()

class Subscriber:
    """
    RabbitMQ stream subscriber.

    A stream subscriber holds information about RabbitMQ stream
    subscription and is used to iterate over messages read from a stream.

    :var client: RabbitMQ Streams client.
    :var stream: RabbitMQ stream name.
    :var subscription_id: RabbitMQ stream subscription id.
    :var offset: RabbitMQ Streams offset specification.
    :var timeout: Raise timeout error if no message within specified time
        (in seconds).
    :var message: Last received message or null.
    :var amqp: Messages are in AMQP 1.0 format if true. Otherwise no AMQP
        decoding.
    """
    def __init__(
        self,
        client,
        stream: str,
        subscription_id: int,
        offset: Offset,
        timeout: float,
        amqp: bool,
    ) -> None:
        """
        Create RabbitMQ stream subscriber.
        """
        self.client = client
        self.stream = stream
        self.subscription_id = subscription_id
        self.offset = offset
        self.timeout = timeout
        self.amqp = amqp
        self.message: MessageCtx | None = None

        self._buffer = deque

    async def __aiter__(self) -> tp.AsyncIterator[MessageCtx]:
        """
        Iterate over messages read from a stream.
        """
        timeout = self.timeout
        client = self.client
        while True:
            try:
                protocol = await client.get_protocol()
                task = protocol.read_stream(self.subscription_id)
                if timeout:
                    task = asyncio.wait_for(task, timeout)
                messages = await task
            except ConnectionError:
                pass
            else:
                while messages:
                    self.message = messages.popleft()
                    yield self.message

# vim: sw=4:et:ai
