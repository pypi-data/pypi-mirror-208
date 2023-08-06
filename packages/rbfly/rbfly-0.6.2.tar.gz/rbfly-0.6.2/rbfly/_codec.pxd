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

from libc.stdint cimport uint16_t, uint32_t, uint64_t

cdef:
    uint16_t unpack_uint16(const char*)
    uint32_t unpack_uint32(const char*)
    uint64_t unpack_uint64(const char*)
    float unpack_float(char*)
    double unpack_double(char*)

    void pack_uint16(char*, uint16_t)
    void pack_uint32(char*, uint32_t)
    void pack_uint64(char*, uint64_t)
    void pack_double(char*, double)

# vim: sw=4:et:ai
