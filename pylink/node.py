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
from .websocket import Websocket
from urllib.parse import quote


class Node:
    def __init__(self, host: str, port: int, password: str, userID: str, identifier: str):
        self._host = host
        self._port = port
        self._password = password
        self._identifier = identifier
        self._websocket = Websocket(host, port, password, userID)

    def __repr__(self):
        return f"<Pylink Node (Identifier={self._identifier})>"

    async def getTracks(self, query: str):
        destination = f"http://{self._host}:{self._port}/loadtracks?identifier={quote(query)}"
        headers = {
            "Authorization": self._password
        }
        async with await self._websocket.get(destination, headers) as req:
            if req.status == 200:
                return await req.json()

    async def send(self, payload):
        await self._websocket.send(payload)
