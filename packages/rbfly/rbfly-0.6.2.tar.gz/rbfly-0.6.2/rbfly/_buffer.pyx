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
Functions to access data in data buffer structure and check its properties.
"""

from .error import RbFlyBufferError

from libc.stdint cimport uint8_t, uint32_t

cdef char* buffer_claim(Buffer *buffer, Py_ssize_t size) except *:
    """
    Get buffer at current offset and increase offset by `size` number.
    """
    cdef Py_ssize_t offset = buffer[0].offset  # current offset

    if not buffer_check_size(buffer, size):
        raise RbFlyBufferError(
            'Buffer too short, offset={}, size={}, value size={}'
            .format(offset, buffer.size, size)
        )

    buffer[0].offset += size  # increased offset
    return &buffer[0].buffer[offset]  # return at current offset

cdef inline uint8_t buffer_get_uint8(Buffer *buffer) except *:
    """
    Get unsigned byte value at current offset and increase offset by 1.
    """
    return <uint8_t> buffer_claim(buffer, 1)[0]

cdef inline char buffer_check_size(Buffer *buffer, uint32_t size):
    """
    Check if buffer allows to access `size` bytes from current offset.
    """
    return buffer[0].offset + size <= buffer[0].size

# vim: sw=4:et:ai
