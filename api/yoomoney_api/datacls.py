import dataclasses

import aiohttp

@dataclasses.dataclass(frozen=True)
class Receiver:
    """Получатель средств"""
    telegram_id: int
    telegram_username: str
    reactions_count: int
    yoomoney_account: str



@dataclasses.dataclass(frozen=True)
class ServerResponse:
    """Ответ сервера (наиболее необходимые компоненты)"""
    result: aiohttp.ClientResponse
    json: dict
    text: str
