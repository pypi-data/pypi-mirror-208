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
Classes and functions, optimized for performance, for RabbitMQ Streams
protocol encoding and decoding.
"""

import array
import logging
import typing as tp
import zlib
from libc.string cimport memcpy
from libc.stdint cimport uint64_t, uint32_t, uint16_t
from cpython cimport array

from ..error import RbFlyBufferError, AMQPDecoderError
from ._mqueue import MessageQueue
from .const import VERSION, KEY_PUBLISH
from .error import ProtocolError

from .._buffer cimport Buffer, buffer_claim, buffer_check_size
from ..amqp._message cimport MessageCtx, c_encode_amqp, c_decode_amqp
from .._codec cimport pack_uint16, pack_uint32, pack_uint64, unpack_uint16, \
    unpack_uint32, unpack_uint64

logger = logging.getLogger(__name__)

cdef enum:
    LEN_FRAME_SIZE = sizeof(uint32_t)

ctypedef Py_ssize_t (*t_func_encode)(Buffer*, object) except -1
ctypedef MessageCtx (*t_func_decode)(Buffer*)

cdef array.array TEMPLATE_MESSAGE_ID = array.array('Q', [])

cdef class FrameDecoder:
    """
    RabbitMQ Streams protocol frame decoder.

    :var data: Buffer receiving data.
    """
    cdef:
        public bytes data

    def __cinit__(self) -> None:
        self.data = b''

    def commands(self, chunk: bytes) -> tp.Iterator:  # [tuple[int, int]]:
        """
        Iterate over indices of each frame in the data buffer. 

        Return RabbitMQ Streams command key with each index.

        Only indices for full frames are returned. If an incomplete frame
        data is kept in the buffer, then the method needs to be called
        again with new chunk data to complete the frame.

        Version of RabbitMQ Streams protocol command is parsed by the
        method. If version does not match supported version, then this fact
        is logged with a warning and the frame is skipped.

        :param chunk: New chunk of data to update existing data buffer.
        """
        cdef Py_ssize_t start, offset, end
        cdef Py_ssize_t data_size
        cdef uint32_t frame_size
        cdef char* data
        cdef uint16_t key, version

        self.data += chunk
        data = <char*> self.data
        data_size = len(self.data)
        offset = 0
        while offset + LEN_FRAME_SIZE <= data_size:
            frame_size = unpack_uint32(&data[offset])

            start = offset + LEN_FRAME_SIZE
            end = start + frame_size
            if end <= data_size:
                key = unpack_uint16(&data[start])
                version = unpack_uint16(&data[start + 2])
                if version == 1:
                    yield start, key
                else:
                   logger.warning(
                       'unknown frame version; version={}'.format(version)
                   )
            else:
                break
            offset = end

        self.data = self.data[offset:]

cdef class FrameEncoder:
    """
    RabbitMQ Streams protocol frame encoder.
    """
    cdef array.array buffer
    cdef char *mv
    cdef int size

    def __cinit__(self, int size):
        # check encoding method if this changes
        if size < 32:
            raise ValueError('Encoder buffer minimum size is 32 bytes')

        self.buffer = array.array('b', [0] * size)
        self.size = size

    def encode(self, data: bytes) -> bytes:
        """
        Encode RabbitMQ Streams protocol frame.
        """
        cdef:
            Py_ssize_t size = len(data)
            Py_ssize_t blen = LEN_FRAME_SIZE + size
            char *bp = self.buffer.data.as_chars

        if blen <= self.size:
            pack_uint32(bp, size)
            memcpy(&bp[LEN_FRAME_SIZE], <char*> data, size)
        else:
            # TODO: how this should fit into RbFlyBufferError and
            # AMQP*Error?
            raise ProtocolError(0x0e, 'Frame too large')

        return bp[:blen]

    def encode_publish(
            self,
            publisher_id: int,
            message_id: uint64_t,
            *messages: MessageCtx | bytes,
            amqp: bool=True,
    ) -> tuple[int, bytes]:
        """
        Encode frame with publish RabbitMQ Streams protocol command.

        :param publisher_id: Publisher id.
        :param message_id: Starting message id of published messages.
        :param messages: List of messages to be published to a stream.
        """
        cdef:
            Buffer b = Buffer(self.buffer.data.as_chars, self.size, 0)
            Buffer *buffer = &b
            char *bp_hdr, *bp_msg
            Py_ssize_t offset = LEN_FRAME_SIZE

            uint64_t start_mid = message_id
            t_func_encode encode_msg = c_encode_amqp if amqp else encode_body

            Py_ssize_t i, count
            object msg
            Py_ssize_t msg_size, msg_len
            Py_ssize_t last_offset, num_offset, frame_size

        msg_len = len(messages)
        bp_hdr = buffer.buffer

        # buffer is 32 bytes long at least, so no buffer bounds checking
        # here
        pack_uint16(&bp_hdr[offset], KEY_PUBLISH)
        offset += sizeof(uint16_t)

        pack_uint16(&bp_hdr[offset], VERSION)
        offset += sizeof(uint16_t)

        bp_hdr[offset] = publisher_id
        offset += 1

        # mark buffer position for number of messages
        num_offset = offset
        offset += sizeof(uint32_t)

        buffer.offset = offset
        for i in range(msg_len):
            msg = messages[i]
            # mark offset of last message, which was successfuly encoded
            last_offset = buffer.offset

            try:
                # pack message id
                bp_msg = buffer_claim(buffer, sizeof(uint64_t))
                pack_uint64(bp_msg, start_mid + i)

                # pack message itself and then its size
                bp_msg = buffer_claim(buffer, sizeof(uint32_t))
                msg_size = encode_msg(buffer, msg)
                pack_uint32(bp_msg, msg_size)
            except RbFlyBufferError as ex:
                count = i
                break
        else:
            count = msg_len
            last_offset = buffer.offset

        pack_uint32(&bp_hdr[num_offset], count)  # TODO: int32 really

        frame_size = last_offset - LEN_FRAME_SIZE
        pack_uint32(buffer.buffer, frame_size)
        return count, buffer.buffer[:last_offset]

def decode_publish_confirm(buffer: bytes, start: int) -> tuple[int, int, int]:
    """
    Decode publisher id and published messages ids from confirmation data
    sent by RabbitMQ Streams broker.

    :param buffer: Published messages confirmation data.
    :param start: Starting point in the buffer. Points to publisher id.
    """
    cdef char publisher_id
    cdef uint32_t n
    cdef Py_ssize_t offset = start
    cdef uint32_t i
    cdef char* data = buffer
    cdef uint64_t first
    cdef uint64_t last

    publisher_id = data[offset]
    offset += 1

    n = unpack_uint32(&data[offset])  # TODO: int32 really
    offset += sizeof(uint32_t)
    assert n > 0  # TODO: no data, raise error

    cdef array.array result = array.clone(TEMPLATE_MESSAGE_ID, n, zero=False)
    cdef uint64_t* mv = <uint64_t*> result.data.as_ulongs

    for i in range(n):
        mv[i] = unpack_uint64(&data[offset])
        offset += sizeof(uint64_t)
        if i > 0:
            assert mv[i - 1] + 1 == mv[i], 'wrong assumptions about message ids'

    first = result[0]
    last = result[0] if n == 1 else result[n - 1]

    return publisher_id, first, last

def decode_messages(
        data: bytes,
        start: int,
        offset_start: tp.Optional[int],
        queue: MessageQueue,
        amqp: bool
) -> None:
    """
    Decode message data received from RabbitMQ Streams broker.

    :param buffer: Data received from RabbitMQ Streams broker.
    :param start: Starting point in the buffer. Points to start of Osiris
        chunk.
    :param offset_start: Value of RabbitMQ Streams offset.
    :param: queue: Message queue to fill with received messages.
    """
    cdef:
        Buffer b = Buffer(data, len(data), start)
        Buffer *buffer = &b
        Py_ssize_t offset = 0
        Py_ssize_t hlen = (
            2
            + sizeof(uint16_t)  # num_entries
            + sizeof(uint32_t)  # num_records
            + sizeof(uint64_t)  * 3  # chunk_first_offset
            + sizeof(uint32_t)  * 4  # reserved
        )
        char *bp

        signed char magic_version, chunk_type
        uint16_t num_entries
        uint32_t num_records, chunk_crc, calc_crc, size, data_size
        uint64_t timestamp, epoch, chunk_first_offset, current_offset

        MessageCtx msg
        t_func_decode decode_msg = c_decode_amqp if amqp else decode_body

    bp = buffer_claim(buffer, hlen)
    magic_version = bp[offset]
    offset += 1
    if magic_version != 0x50:  # or 'P'
        logger.warning('unknown magic version: 0x{:02x}'.format(magic_version))
        return

    chunk_type = bp[offset]
    offset += 1

    num_entries = unpack_uint16(&bp[offset])
    offset += sizeof(uint16_t)

    num_records = unpack_uint32(&bp[offset])
    offset += sizeof(uint32_t)

    timestamp = unpack_uint64(&bp[offset])
    offset += sizeof(uint64_t)

    epoch = unpack_uint64(&bp[offset])
    offset += sizeof(uint64_t)

    chunk_first_offset = unpack_uint64(&bp[offset])
    offset += sizeof(uint64_t)

    # offset: 32
    chunk_crc = unpack_uint32(&bp[offset])
    offset += sizeof(uint32_t)

    data_size = unpack_uint32(&bp[offset])
    offset += sizeof(uint32_t)

    offset += sizeof(uint32_t) * 2  # skip for the fields below
    # trailer_len = unpack_uint32(&bp[offset])
    # offset += sizeof(uint32_t)
    # reserved = unpack_uint32(&bp[offset])
    # offset += sizeof(uint32_t)

    if not buffer_check_size(buffer, data_size):
        logger.warning(
            'chunk data size invalid, chunk first offset={},'
            ' timestamp={}, data size={}, buffer size={}'.format(
                chunk_first_offset,
                timestamp,
                data_size,
                buffer.size
            )
        )
        return

    calc_crc = zlib.crc32(bp[offset:offset + data_size])
    if chunk_crc != calc_crc:
        logger.warning(
            'chunk crc validation failed, chunk first offset={},'
            ' timestamp={}, crc={}'.format(
                chunk_first_offset, timestamp, calc_crc
            )
        )
        return

    for i in range(num_entries):
        bp = buffer_claim(buffer, sizeof(uint32_t))
        size = unpack_uint32(bp)
        if buffer_check_size(buffer, size):
            current_offset = chunk_first_offset + i
            if offset_start is None or current_offset >= offset_start:
                try:
                    msg = decode_msg(buffer)
                    msg.stream_offset = current_offset
                    msg.stream_timestamp = <double> timestamp / 1000
                except AMQPDecoderError as ex:
                    logger.warning('cannot decode amqp message: {}'.format(ex))
                else:
                    queue.put(msg)
            else:
                buffer.offset += size  # skip message
        else:
            logger.warning(
                'message data size invalid, chunk first offset={},'
                ' timestamp={}, offset={}, message size={}, buffer size={}'.format(
                    chunk_first_offset,
                    timestamp,
                    buffer.offset,
                    size,
                    buffer.size
                )
            )
            return

cdef inline Py_ssize_t encode_body(Buffer *buffer, object message) except -1:
    cdef:
        Py_ssize_t size = len(message)
        char *bp

    bp = buffer_claim(buffer, size)
    memcpy(bp, <char*> message, size)
    return size

cdef inline MessageCtx decode_body(Buffer *buffer):
    return MessageCtx(buffer.buffer[buffer.offset:buffer.size])

# vim: sw=4:et:ai
