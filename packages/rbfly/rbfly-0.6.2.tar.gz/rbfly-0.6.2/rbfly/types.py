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
Basic types.
"""

import uuid
import typing as tp
from collections.abc import Sequence
from datetime import datetime

class Symbol:
    """
    Symbolic value from a constrained domain as defined by AMQP 1.0.
    """
    __slots__ = ['name']
    __cache__: dict[str, 'Symbol'] = {}

    def __new__(cls, name: str) -> 'Symbol':
        if name not in Symbol.__cache__:
            Symbol.__cache__[name] = object.__new__(cls)
        return Symbol.__cache__[name]

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return 'Symbol<{}>'.format(self.name)

AMQPScalar: tp.TypeAlias = str | bool | int | float | datetime \
    | uuid.UUID | Symbol | bytes
AMQPSequence: tp.TypeAlias = Sequence['AMQPBody']
AMQPMap: tp.TypeAlias = dict['AMQPBody', 'AMQPBody']

#: Type for AMQP message sent by a publisher or received by a subscriber.
AMQPBody: tp.TypeAlias = AMQPSequence | AMQPMap | AMQPScalar

__all__ = ['AMQPBody', 'Symbol']

# vim: sw=4:et:ai
