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

import typing as tp

from ..amqp import MessageCtx
from ._mqueue import MessageQueue

class FrameDecoder:
    data: bytes
    def __init__(self) -> None: ...
    def commands(self, chunk: bytes) -> tp.Iterator[tuple[int, int]]: ...

class FrameEncoder:
    def __init__(self, size: int): ...

    def encode(self, data: bytes) -> bytes: ...

    def encode_publish(
            self,
            publisher_id: int,
            message_id: int,
            *messages: MessageCtx | bytes,
            amqp: bool=True
    ) -> tuple[int, bytes]:
        ...

def decode_publish_confirm(buffer: bytes, start: int) -> tuple[int, int, int]:
    ...

def decode_messages(
        buffer: bytes,
        start: int,
        offset: tp.Optional[int],
        queue: MessageQueue,
        amqp: bool
) -> None:
    ...

# vim: sw=4:et:ai
