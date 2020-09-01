import requests
import aiohttp
import asyncio
from abc import abstractmethod, ABC


class IEX(ABC):
    def __init__(self, base, token):
        self.base = base
        self.token = token

    async def request(self, url, params, session):
        try:
            url = f"{self.base}/{url}"
            r = await session.get(url, params=params)
            return await r.json()
        except:
            return

