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
Unit tests for creating RabbitMQ Streams client.
"""

import asyncio
import copy
import inspect
import typing as tp
from collections.abc import AsyncIterator, AsyncGenerator
from functools import partial

from rbfly.error import RbFlyError
from rbfly.streams.client import Scheme, StreamsClient, streams_client, \
    connection
from rbfly.streams._client import PublisherTrait, Publisher, PublisherBatch, \
    PublisherBatchMem, PublisherBin, PublisherBinBatch
from rbfly.streams.offset import Offset, OffsetType
from rbfly.streams.protocol import ProtocolError

import pytest
from unittest import mock

TEST_CLIENT_URI = [
    (
        'rabbitmq-stream://',
        Scheme.RABBITMQ_STREAM, 'localhost', 5552, '/', None, None
    ),
    (
        'rabbitmq-stream://localhost',
        Scheme.RABBITMQ_STREAM, 'localhost', 5552, '/', None, None
    ),
    (
        'rabbitmq-stream://localhost/',
        Scheme.RABBITMQ_STREAM, 'localhost', 5552, '/', None, None
    ),
    (
        'rabbitmq-stream://some-server:1002/a-vhost',
        Scheme.RABBITMQ_STREAM, 'some-server', 1002, 'a-vhost', None, None
    ),
    (
        'rabbitmq-stream+tls://some-server',
        Scheme.RABBITMQ_STREAM_TLS, 'some-server', 5551, '/', None, None
    ),
    (
        'rabbitmq-stream://user@some-server',
        Scheme.RABBITMQ_STREAM, 'some-server', 5552, '/', 'user', None
    ),
    (
        'rabbitmq-stream://user:passta@some-server/tsohvvhost',
        Scheme.RABBITMQ_STREAM, 'some-server', 5552, 'tsohvvhost', 'user', 'passta'
    ),
]

TEST_MESSAGE_ID = [
    (2 ** 31 - 1, 2 ** 31),
    (2 ** 32 - 1, 2 ** 32),
    (2 ** 63 - 1, 2 ** 63),
]

@pytest.mark.parametrize(
    'uri, scheme, host, port, vhost, user, password',
    TEST_CLIENT_URI
)
def test_create_client(
        uri: str,
        scheme: Scheme,
        host: str,
        port: int,
        vhost: str,
        user: tp.Optional[str],
        password: tp.Optional[str],
) -> None:
    """
    Test creating RabbitMQ Streams client from URI.
    """
    # pylint: disable=protected-access

    client = streams_client(uri)
    assert client._cinfo.scheme == scheme
    assert client._cinfo.host == host
    assert client._cinfo.port == port
    assert client._cinfo.virtual_host == vhost
    assert client._cinfo.username == user
    assert client._cinfo.password == password

@pytest.mark.asyncio
async def test_get_offset_reference() -> None:
    """
    Test getting offset specification for RabbitMQ stream with offset
    reference.
    """
    # pylint: disable=protected-access

    client = streams_client('rabbitmq-stream://')
    protocol = mock.MagicMock()
    client.get_protocol = mock.AsyncMock(return_value=protocol)  # type: ignore
    protocol.query_offset = mock.AsyncMock(return_value=5)

    offset = Offset.reference('ref-a')
    result = await client._get_offset_reference('a-stream', offset)

    assert result.type == OffsetType.OFFSET
    assert result.value == 6
    protocol.query_offset.assert_called_once_with('a-stream', 'ref-a')

@pytest.mark.asyncio
async def test_get_offset_reference_zero() -> None:
    """
    Test getting offset specification for RabbitMQ stream with offset
    reference, when reference is not stored yet.
    """
    # pylint: disable=protected-access

    client = streams_client('rabbitmq-stream://')
    protocol = mock.MagicMock()
    client.get_protocol = mock.AsyncMock(return_value=protocol)  # type: ignore
    protocol.query_offset = mock.AsyncMock(side_effect=ProtocolError(0x13))

    offset = Offset.reference('ref-a')
    result = await client._get_offset_reference('a-stream', offset)

    assert result.type == OffsetType.OFFSET
    assert result.value == 0
    protocol.query_offset.assert_called_once_with('a-stream', 'ref-a')

@pytest.mark.asyncio
async def test_get_offset() -> None:
    """
    Test getting offset specification for RabbitMQ stream using offset
    value (not using offset reference).
    """
    # pylint: disable=protected-access

    client = streams_client('rabbitmq-stream://')
    protocol = mock.MagicMock()
    client.get_protocol = mock.AsyncMock(return_value=protocol)  # type: ignore

    offset = Offset.offset(0)
    result = await client._get_offset_reference('a-stream', offset)

    assert result == offset
    assert not protocol.query_offset.called

def test_publisher_trait() -> None:
    """
    Test publisher trait message id functionality.
    """
    client = mock.MagicMock()
    publisher = PublisherTrait(client, 'a-stream', 3, 'pub-name', 11)

    assert publisher.stream == 'a-stream'
    assert publisher.id == 3
    assert publisher.next_message_id() == 12

@pytest.mark.parametrize('start_mid, expected', TEST_MESSAGE_ID)
def test_publisher_trait_next_message(start_mid: int, expected: int) -> None:
    """
    Test publisher trait message id overflow.
    """
    assert start_mid >= 0 and expected >= 0
    client = mock.MagicMock()
    publisher = PublisherTrait(client, 'a-stream', 3, 'pub-name', start_mid)
    assert publisher.next_message_id() == expected

@pytest.mark.asyncio
async def test_publisher_send_amqp() -> None:
    """
    Test publisher sending AMQP message.
    """
    client = mock.AsyncMock()
    protocol = await client.get_protocol()

    publisher = Publisher(client, 'stream', 2, 'pub-name', 11)
    await publisher.send(b'12345')

    #expected_msg = b'\x00Su\xa0\x0512345'
    protocol.publish.assert_called_once_with(2, 11, mock.ANY, amqp=True)
    # last message id is increased by 1
    assert publisher.message_id == 12

@pytest.mark.asyncio
async def test_publisher_send_amqp_batch() -> None:
    """
    Test publisher sending batch of AMQP message.
    """
    # pylint: disable=protected-access

    client = mock.AsyncMock()
    protocol = await client.get_protocol()
    protocol.publish = mock.AsyncMock(return_value=2)

    publisher = PublisherBatch(client, 'stream', 2, 'pub-name', 11)
    publisher.batch(b'12345')
    publisher.batch(b'54321')
    await publisher.flush()

    #expected_msg = [b'\x00Su\xa0\x0512345', b'\x00Su\xa0\x0554321']
    protocol.publish.assert_called_once_with(2, 11, mock.ANY, mock.ANY, amqp=True)

    # last message id is increased by 2
    assert publisher.message_id == 13
    assert publisher._data == []

@pytest.mark.asyncio
async def test_publisher_send_mem_batch() -> None:
    """
    Test publisher sending batch of AMQP message with memory protection.
    """
    # pylint: disable=protected-access

    client = mock.AsyncMock()
    await client.get_protocol()

    publisher = PublisherBatchMem(client, 'stream', 2, 'pub-name', 11)
    await publisher.batch(b'12345', max_len=3)
    await publisher.batch(b'54321', max_len=3)
    await publisher.batch(b'54321', max_len=3)

    # batch blocks due to max_len == 3
    with pytest.raises(asyncio.TimeoutError) as ex_ctx:
        await asyncio.wait_for(publisher.batch(b'54321', max_len=3), 0.1)

    assert type(ex_ctx.value) == asyncio.TimeoutError

    # data flushed...
    await publisher.flush()
    assert len(publisher._data) == 0

    # ... so can batch again
    await publisher.batch(b'54321', max_len=3)
    assert len(publisher._data) == 1

@pytest.mark.asyncio
async def test_publisher_send_binary() -> None:
    """
    Test publisher sending opaque binary data.
    """
    client = mock.AsyncMock()
    protocol = await client.get_protocol()

    publisher = PublisherBin(client, 'stream', 2, 'pub-name', 12)
    await publisher.send(b'12345')

    # last message id is increased by 1
    protocol.publish.assert_called_once_with(2, 12, b'12345', amqp=False)
    assert publisher.message_id == 13

@pytest.mark.asyncio
async def test_publisher_send_batch_binary() -> None:
    """
    Test publisher sending batch of binary data.
    """
    # pylint: disable=protected-access,unnecessary-lambda-assignment

    client = mock.AsyncMock()
    protocol = await client.get_protocol()

    publisher = PublisherBinBatch(client, 'stream', 2, 'pub-name', 11)
    publisher.batch(b'12345')
    publisher.batch(b'54321')

    # workaround for mutable PubBatchBinary._data being passed to
    # `protocol.publish`
    call_recorder = []
    record = lambda *args, **kw: call_recorder.append((
        [copy.copy(a) for a in args],
        kw
    ))
    protocol.publish.side_effect = record
    await publisher.flush()

    protocol.publish.assert_called_once()
    assert call_recorder == [([2, 11, b'12345', b'54321'], {'amqp': False})]

    # last message id is increased by 2
    assert publisher.message_id == 13
    assert publisher._data == []

def test_connection_coroutine() -> None:
    """
    Test if connection decorator returns coroutine function.
    """
    # pylint: disable=invalid-name

    async def f() -> None:
        pass

    assert inspect.iscoroutinefunction(connection(f))
    assert inspect.iscoroutinefunction(connection(partial(f)))

@pytest.mark.asyncio
async def test_connection_async_iterator() -> None:
    """
    Test if connection decorator returns asynchronous iterator function.
    """
    # pylint: disable=invalid-name,unused-argument

    async def fx(client: StreamsClient) -> AsyncIterator[int]:
        for i in range(10):
            yield i
            await asyncio.sleep(0.001)

    assert inspect.isasyncgenfunction(connection(fx))
    assert inspect.isasyncgenfunction(connection(partial(fx)))

    client = mock.AsyncMock()
    coro = connection(fx)(client)
    result = [v async for v in coro]
    assert result == list(range(10))
    client.disconnect.assert_called_once()

# TODO: make connection decorator work with generators receiving data via
# yield
@pytest.mark.skip
@pytest.mark.asyncio
async def test_connection_async_generator_yield() -> None:
    """
    Test if connection decorator returns asynchronous generator function
    which accepts data with `asend` method.
    """
    # pylint: disable=invalid-name,unused-argument

    @connection
    async def fx(client: StreamsClient, data: list[int]) -> AsyncGenerator[None, int]:
        while True:
            value = yield
            data.append(value)
            await asyncio.sleep(0.1)

    assert inspect.isasyncgenfunction(fx)

    client = mock.AsyncMock()
    data: list[int] = []

    f = fx(client, data)
    await f.asend(None)
    await f.asend(1)
    await f.asend(2)
    await f.asend(3)
    await f.aclose()

    assert data == [1, 2, 3]
    client.disconnect.assert_called_once()

def test_connection_invalid() -> None:
    """
    Test if error is raised by connection decorator for non-asynchronous
    function.
    """
    # pylint: disable=invalid-name

    def f() -> None:
        pass

    with pytest.raises(RbFlyError):
        # `f` is not valid function from type checks point of view as well
        connection(f)  # type: ignore

# vim: sw=4:et:ai
