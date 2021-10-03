"""
Copyright (C) 2021 Aspect1103

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
import aiohttp
from urllib.parse import quote
from typing import Union

from discord.enums import VoiceRegion
from discord.ext.commands import Bot, AutoShardedBot

from .websocket import Websocket


class Node:
    def __init__(self, bot: Union[Bot, AutoShardedBot], host: str, port: int, password: str, region: VoiceRegion, identifier: str) -> None:
        self.bot = bot
        self.host = host
        self.port = port
        self.password = password
        self.region = region
        self.identifier = identifier
        self.session = aiohttp.ClientSession()
        self.playerCount = 0
        self._websocket = None

    def __repr__(self) -> str:
        return f"<Pylink Node (Domain={self.host}:{self.port}) (Identifier={self.identifier}) (Region={self.region})>"

    async def connect(self):
        self._websocket = Websocket(self)

    async def getTracks(self, query: str) -> dict:
        destination = f"http://{self.host}:{self.port}/loadtracks?identifier={quote(query)}"
        headers = {
            "Authorization": self.password
        }
        async with await self._websocket.get(destination, headers) as req:
            if req.status == 200:
                return await req.json()

    async def send(self, payload: dict) -> None:
        await self._websocket.send(payload)
