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
import asyncio
from typing import Dict, Any
from aiohttp.client_reqrep import ClientResponse


class Websocket:
    def __init__(self, node) -> None:
        self.node = node
        self.open = False
        self.connected = False
        self._connection = None
        self._listener = None
        asyncio.create_task(self.connect())

    def isConnected(self):
        return self.isConnected and self.open

    async def connect(self) -> None:
        headers = {
            "Authorization": self.node.password,
            "User-Id": str(self.node.bot.user.id),
            "Client-Name": "Pylink"
        }
        self._connection = await self.node.session.ws_connect(f"ws://{self.node.host}:{self.node.port}", headers=headers, heartbeat=60)
        self._listener = self.node.bot.loop.create_task(self.listener())
        self.connected = True
        self.open = True

    async def listener(self) -> None:
        while True:
            msg = await self._connection.receive()
            await self.processListener(msg.json())
            await asyncio.sleep(30)

    async def processListener(self, data: Dict[str, Any]):
        op = data.get("op")
        if op == "stats":
            return
        elif op == "playerUpdate":
            # TODO: Implement
            return
        elif op == "event":
            # TODO: Implement
            return

    async def get(self, destination: str, headers: Dict[str, str]) -> ClientResponse:
        return await self.node.session.get(destination, headers=headers)

    async def send(self, payload: dict) -> None:
        await self._connection.send_json(payload)
