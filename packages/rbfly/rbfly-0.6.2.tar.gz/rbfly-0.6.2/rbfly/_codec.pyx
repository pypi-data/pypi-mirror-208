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
Basic function to encode and decode binary formats.
"""

from libc.stdint cimport uint16_t, uint32_t, uint64_t

cdef extern from "arpa/inet.h":
    uint32_t ntohl(uint32_t)
    uint16_t ntohs(uint16_t)

    uint32_t htonl(uint32_t)
    uint32_t htons(uint16_t)

cdef extern from "_codec.h":
    uint64_t be64toh(uint64_t)
    uint64_t htobe64(uint64_t)

cdef union u32dcast:
    uint64_t u32
    float f32

cdef union u64dcast:
    uint64_t u64
    double d64

cdef inline uint16_t unpack_uint16(const char* data):
    return ntohs((<uint16_t*> data)[0])

cdef inline uint32_t unpack_uint32(const char* data):
    return ntohl((<uint32_t*> data)[0])

cdef inline uint64_t unpack_uint64(const char* data):
    return be64toh((<uint64_t*> data)[0])

cdef inline float unpack_float(const char* data):
    assert sizeof(float) == sizeof(uint32_t)
    return u32dcast(u32=unpack_uint32(data)).f32

cdef inline double unpack_double(const char* data):
    assert sizeof(double) == sizeof(uint64_t)
    return u64dcast(u64=unpack_uint64(data)).d64

cdef inline void pack_uint16(char* data, uint16_t value):
    (<uint16_t*> data)[0] = htons(<uint16_t> value)

cdef inline void pack_uint32(char* data, uint32_t value):
    (<uint32_t*> data)[0] = htonl(value)

cdef inline void pack_uint64(char* data, uint64_t value):
    (<uint64_t*> data)[0] = htobe64(value)

cdef inline void pack_double(char* data, double value):
    assert sizeof(double) == sizeof(uint64_t)
    pack_uint64(data, u64dcast(d64=value).u64)

# vim: sw=4:et:ai
