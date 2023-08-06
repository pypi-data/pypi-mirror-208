import typing as tp

from ..types import AMQPBody
from ..amqp import MessageCtx
from .client import StreamsClient
from .offset import Offset

class PublisherConstr(tp.Protocol):
    id: int
    name: str
    stream: str

    def __init__(
        self,
        client: StreamsClient, stream: str, id: int, name: str, message_id: int
    ) -> None: ...

class PublisherTrait:
    stream: str
    id: int
    message_id: int

    def __init__(
        self,
        client: StreamsClient, stream: str, id: int, name: str, message_id: int
    ) -> None: ...

    def next_message_id(self) -> int: ...

class Publisher(PublisherTrait):
    async def send(self, body: AMQPBody) -> None: ...

class PublisherBatch(PublisherTrait):
    _data: list[bytes]

    def batch(self, body: AMQPBody) -> None: ...

    async def flush(self) -> None: ...

class PublisherBatchMem(PublisherTrait):
    _data: list[bytes]

    async def batch(self, body: AMQPBody, *, max_len: int) -> None: ...

    async def flush(self) -> None: ...

class PublisherBin(PublisherTrait):
    async def send(self, message: bytes) -> None: ...

class PublisherBinBatch(PublisherTrait):
    _data: list[bytes]

    def batch(self, message: bytes) -> None: ...

    async def flush(self) -> None: ...

class Subscriber:
    stream: str
    subscription_id: int
    offset: Offset
    timeout: float
    amqp: bool
    message: MessageCtx | None

    def __init__(
        self,
        client: StreamsClient,
        stream: str,
        subscription_id: int,
        offset: Offset,
        timeout: float,
        amqp: bool,
    ) -> None:
        ...

    def __aiter__(self) -> tp.AsyncIterator[MessageCtx]: ...

# vim: sw=4:et:ai
