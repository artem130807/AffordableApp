from typing import Protocol


class DatabaseHealthPort(Protocol):
    async def is_ready(self) -> bool: ...
