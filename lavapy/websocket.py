"""
MIT License

Copyright (c) 2021-present Aspect1103

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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
            "Client-Name": "Lavapy"
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
