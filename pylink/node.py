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
from urllib.parse import quote

from discord.enums import VoiceRegion

from .websocket import Websocket


class Node:
    def __init__(self, client, host: str, port: int, password: str, region: VoiceRegion, identifier: str) -> None:
        self.client = client
        self.host = host
        self.port = port
        self.password = password
        self.region = region
        self.identifier = identifier
        self.playerCount = 0
        self._websocket = Websocket(self)

    def __repr__(self) -> str:
        return f"<Pylink Node (Domain={self.host}:{self.port}) (Identifier={self.identifier}) (Region={self.region})>"

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
