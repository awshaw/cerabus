import asyncio
import sys

import aiohttp
from aiohttp import ClientSession

from iex import IEX

if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Options(IEX):
    async def get_expirations(self, symbols):
        async with ClientSession() as session:
            for symbol in symbols:
                url = f"stock/{symbol}/options"
                params = {"token": self.token}
                print(await self.request(url, params, session))