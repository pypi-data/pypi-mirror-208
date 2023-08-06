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

from libc.stdint cimport uint8_t, uint32_t

cdef:
    # Structure to track status of a data buffer.
    #
    # Data buffer is an array of bytes of certain size. Offset attribute
    # is used to track current position when decoding data from the
    # buffer or encoding data into the buffer.
    #
    # Invariants:
    #
    # - buffer != NULL
    # - size > 0
    # - offset >= 0
    # - offset < size
    struct Buffer:
        char *buffer
        Py_ssize_t size
        Py_ssize_t offset


    char* buffer_claim(Buffer*, Py_ssize_t) except *
    uint8_t buffer_get_uint8(Buffer*) except *
    char buffer_check_size(Buffer*, uint32_t)

# vim: sw=4:et:ai
