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

import uuid
from datetime import datetime, timezone

from rbfly.amqp._message import MessageCtx, encode_amqp, decode_amqp
from rbfly.types import Symbol
from rbfly.error import RbFlyBufferError, AMQPDecoderError

import pytest

# decoding and encoding of AMQP types in the context of Python objects
DATA = (
    # binary, opaque message (first with nulls in the message)
    (MessageCtx(b'\x01\x00\x00\x00\x02'), b'\x00Su\xa0\x05\x01\x00\x00\x00\x02'),
    (MessageCtx(b'abcde'), b'\x00Su\xa0\x05abcde'),
    (MessageCtx(b'a' * 256), b'\x00Su\xb0\x00\x00\x01\x00' + b'a' * 256),
    # message size > 127 to detect possible signed char mistake
    (MessageCtx(b'a' * 130), b'\x00Su\xa0\x82' + b'a' * 130),

    # string
    (MessageCtx('abcde'), b'\x00Sw\xa1\x05abcde'),
    (MessageCtx('a' * 256), b'\x00Sw\xb1\x00\x00\x01\x00' + b'a' * 256),

    # symbol
    (MessageCtx(Symbol('abcde')), b'\x00Sw\xa3\x05abcde'),
    (MessageCtx(Symbol('a' * 256)), b'\x00Sw\xb3\x00\x00\x01\x00' + b'a' * 256),

    # boolean
    (MessageCtx(True), b'\x00SwA'),
    (MessageCtx(False), b'\x00SwB'),

    # int
    (MessageCtx(-2 ** 31), b'\x00Sw\x71\x80\x00\x00\x00'),
    (MessageCtx(2 ** 31 - 1), b'\x00Sw\x71\x7f\xff\xff\xff'),

    # long
    (MessageCtx(-2 ** 63), b'\x00Sw\x81\x80\x00\x00\x00\x00\x00\x00\x00'),
    (MessageCtx(2 ** 63 - 1), b'\x00Sw\x81\x7f\xff\xff\xff\xff\xff\xff\xff'),

    # ulong
    (MessageCtx(2 ** 64 - 1), b'\x00Sw\x80\xff\xff\xff\xff\xff\xff\xff\xff'),

    # double
    (MessageCtx(201.102), b'\x00Sw\x82@i#C\x95\x81\x06%'),

    # timestamp
    (
        MessageCtx(datetime(2022, 8, 14, 16, 1, 13, 567000, tzinfo=timezone.utc)),
        b'\x00Sw\x83\x00\x00\x01\x82\x9d\x16\x7f_'
    ),

    # uuid
    (MessageCtx(
        uuid.UUID('5c79d81f0a8f4305921abd8f8978a11a')),
        b'\x00Sw\x98\\y\xd8\x1f\n\x8fC\x05\x92\x1a\xbd\x8f\x89x\xa1\x1a'
    ),

    # map
    (
        MessageCtx({'a': 1, 'b': 2}),
        b'\x00Sw\xd1\x00\x00\x00\x10\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
    # nested map
    (
        MessageCtx({'a': 1, 'b': {'a': 1, 'b': 2}}),
        b'\x00Sw\xd1\x00\x00\x00\x24\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\xd1\x00\x00\x00\x10\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
    # a map with binary data
    (
        MessageCtx({b'ab': b'xy'}),
        b'\x00Sw\xd1\x00\x00\x00\x08\x00\x00\x00\x02\xa0\x02ab\xa0\x02xy',
    ),
    # list
    (
        MessageCtx(['a', 1, 'b', 2]),
        b'\x00Sw\xd0\x00\x00\x00\x10\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
    # nested list
    (
        MessageCtx(['a', 1, 'b', ['a', 1, 'b', 2]]),
        b'\x00Sw\xd0\x00\x00\x00\x24\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\xd0\x00\x00\x00\x10\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
    # a list with binary data
    (
        MessageCtx([255, b'abc']),
        b'\x00Sw\xd0\x00\x00\x00\n\x00\x00\x00\x02q\x00\x00\x00\xff\xa0\x03abc',
    )
)

# decoding of AMQP types, which are not encoded by rbfly
DATA_PARSED = (
    # ubyte
    (MessageCtx(255), b'\x00Sw\x50\xff'),

    # ushort
    (MessageCtx(2 ** 16 - 1), b'\x00Sw\x60\xff\xff'),

    # uint, smalluint, uint0
    (MessageCtx(2 ** 32 - 1), b'\x00Sw\x70\xff\xff\xff\xff'),
    (MessageCtx(255), b'\x00Sw\x52\xff'),
    (MessageCtx(0), b'\x00Sw\x43'),

    # ulong, smallulong, ulong0
    (MessageCtx(2 ** 64 - 1), b'\x00Sw\x80\xff\xff\xff\xff\xff\xff\xff\xff'),
    (MessageCtx(255), b'\x00Sw\x53\xff'),
    (MessageCtx(0), b'\x00Sw\x44'),

    # byte
    (MessageCtx(-1), b'\x00Sw\x51\xff'),

    # short
    (MessageCtx(-1), b'\x00Sw\x61\xff\xff'),

    # int, smallint
    (MessageCtx(-1), b'\x00Sw\x71\xff\xff\xff\xff'),
    (MessageCtx(-1), b'\x00Sw\x54\xff'),

    # long
    (MessageCtx(-1), b'\x00Sw\x81\xff\xff\xff\xff\xff\xff\xff\xff'),
    (MessageCtx(-1), b'\x00Sw\x55\xff'),

    # float
    (MessageCtx(201.1020050048828), b'\x00Sw\x72CI\x1a\x1d'),

    # map8
    (
        MessageCtx({'a': 1, 'b': 2}),
        b'\x00Sw\xc1\x10\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
    # list8
    (
        MessageCtx(['a', 1, 'b', 2]),
        b'\x00Sw\xc0\x10\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
    ),
    # list0
    (
        MessageCtx([]),
        b'\x00Sw\x45',
    ),
)

MESSAGE_REPR = (
    (
        MessageCtx('a-string'),
        'MessageCtx(body=\'a-string\', stream_offset=0,' \
            ' stream_timestamp=0.0, annotations={}, app_properties={})',
    ),
    (
        MessageCtx('a-string-and-more', stream_timestamp=2.0),
        'MessageCtx(body=\'a-string-a...\', stream_offset=0,' \
            ' stream_timestamp=2.0, annotations={}, app_properties={})',
    ),
    (
        MessageCtx(b'binary-data-and-more'),
        'MessageCtx(body=b\'binary-dat...\', stream_offset=0,' \
            ' stream_timestamp=0.0, annotations={}, app_properties={})',
    ),
    (
        MessageCtx(15),
        'MessageCtx(body=15, stream_offset=0,' \
            ' stream_timestamp=0.0, annotations={}, app_properties={})',
    ),
    (
        MessageCtx({'a': 15}),
        'MessageCtx(body={\'a\': 15}, stream_offset=0,' \
            ' stream_timestamp=0.0, annotations={}, app_properties={})',
    ),
)

# data for parsing of annotated AMQP messages
DATA_ANNOTATED = (
    # with message annotation
    (
        MessageCtx('ab', annotations={Symbol('a'): 'b', Symbol('c'): 'd'}),
        b'\x00Sr\xc1\x0d\x04\xa3\x01a\xa1\x01b\xa3\x01c\xa1\x01d\x00Sw\xa1\02ab'
    ),
    # with application properties
    (
        MessageCtx('ab', app_properties={Symbol('a'): 'b', Symbol('c'): 'd'}),
        b'\x00St\xc1\x0d\x04\xa3\x01a\xa1\x01b\xa3\x01c\xa1\x01d\x00Sw\xa1\02ab'
    ),
)

DATA_BUFFER_INVALID = (
    # uint32 missing one byte
    b'\x00Sw\x71\x80\x00\x00',
)

DATA_AMQP_INVALID = (
    # minimum 4 bytes expected
    b'\x00Sw',

    # string/byte string: expected buffer size is one more byte
    b'\x00Sw\xa1\x06abcde',

    # size of compound (map) buffer: expected buffer size is one more byte
    b'\x00Sw\xd1\x00\x00\x00\x18\x00\x00\x00\x04\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00',

    # count of compound (map): odd number of elements (3 to be exact) instead of even
    b'\x00Sw\xd1\x00\x00\x00\x18\x00\x00\x00\x03\xa1\x01a\x71\x00\x00\x00\x01\xa1\x01b\x71\x00\x00\x00\x02',
)

@pytest.mark.parametrize('message, expected', DATA)
def test_encode(message: MessageCtx, expected: bytes) -> None:
    """
    Test encoding AMQP messages.
    """
    msg_buffer = bytearray(1024)
    size = encode_amqp(msg_buffer, message)
    assert bytes(msg_buffer[:size]) == expected

@pytest.mark.parametrize('message, data', DATA + DATA_PARSED)
def test_decode(message: MessageCtx, data: bytes) -> None:
    """
    Test decoding AMQP messages.
    """
    result = decode_amqp(data)
    assert result == message

@pytest.mark.parametrize('message, data', DATA_ANNOTATED)
def test_decode_annotated(message: MessageCtx, data: bytes) -> None:
    """
    Test decoding of annotated AMQP messages.
    """
    result = decode_amqp(data)
    assert result == message

@pytest.mark.parametrize('message, expected', MESSAGE_REPR)
def test_message_repr(message: MessageCtx, expected: str) -> None:
    """
    Test AMQP message representation.
    """
    assert repr(message) == expected

@pytest.mark.parametrize('data', DATA_AMQP_INVALID)
def test_decode_invalid_amqp(data: bytes) -> None:
    """
    Test decoding invalid AMQP data.
    """
    with pytest.raises(AMQPDecoderError):
        decode_amqp(data)

# buffer related tests

def test_encode_amqp_string_too_long() -> None:
    """
    Test error when encoding too long string message.
    """
    msg_buffer = bytearray(1024)
    with pytest.raises(RbFlyBufferError):
        encode_amqp(msg_buffer, MessageCtx(b'a' * 2 ** 32))

def test_encode_amqp_list_too_long() -> None:
    """
    Test error when encoding too long list message.
    """
    msg_buffer = bytearray(1024)
    with pytest.raises(RbFlyBufferError):
        encode_amqp(msg_buffer, MessageCtx(list(range(204))))

def test_encode_amqp_dict_too_long() -> None:
    """
    Test error when encoding too long dictionary message.
    """
    msg_buffer = bytearray(1024)
    with pytest.raises(RbFlyBufferError):
        data = dict(zip(range(102), range(102)))
        encode_amqp(msg_buffer, MessageCtx(data))  # type: ignore[arg-type]

@pytest.mark.parametrize('data', DATA_BUFFER_INVALID)
def test_decode_invalid_buffer(data: bytes) -> None:
    """
    Test decoding AMQP data with buffer compromised.
    """
    with pytest.raises(RbFlyBufferError):
        decode_amqp(data)

# vim: sw=4:et:ai
