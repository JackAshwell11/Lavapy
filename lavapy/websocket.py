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
from __future__ import annotations

import asyncio
import logging
from asyncio import Task
from typing import Dict, Any, Optional, TYPE_CHECKING
from aiohttp import WSMsgType
from aiohttp.client_ws import ClientWebSocketResponse

from .backoff import ExponentialBackoff

if TYPE_CHECKING:
    from .node import Node

logger = logging.getLogger(__name__)

__all__ = ("Websocket",)


class Websocket:
    """
    Lavapy Websocket object.

    Attributes
    ----------
    node: Node
        The Lavapy :class:`Node` object which manages this websocket.
    open: bool
        A bool stating whether the connection to Lavalink is open or not.
    connected: bool
        A bool stating if the websocket is connected to Lavalink or not.
    connection: ClientWebSocketResponse
        The actual websocket connection to the Lavalink server.
    """

    def __init__(self, node: Node) -> None:
        self.node: Node = node
        self.open: bool = False
        self.connected: bool = False
        self.connection: Optional[ClientWebSocketResponse] = None
        self._listener: Optional[Task] = None
        asyncio.create_task(self.connect())

    @property
    def isConnected(self) -> bool:
        """Returns whether the websocket is connected or not."""
        return self.connected and self.open

    async def connect(self) -> None:
        """Establishes the connection to the Lavalink server."""
        headers = {
            "Authorization": self.node.password,
            "User-Id": str(self.node.bot.user.id),
            "Client-Name": "Lavapy"
        }
        logger.debug(f"Attempting connection with headers: {headers}")
        self.connection = await self.node.session.ws_connect(f"ws://{self.node.host}:{self.node.port}", headers=headers,
                                                             heartbeat=60)
        self._listener = self.node.bot.loop.create_task(self.listener())
        self.connected = True
        self.open = True
        logger.debug(f"Connection established with node: {self.node.__repr__()}")

    async def disconnect(self):
        """Closes the connection to the Lavalink server."""
        logger.debug(f"Closing connection for node: {self.node.__repr__()}")
        await self.connection.close()
        self.connected = False
        self.open = False

    async def listener(self) -> None:
        """Continuously pings the Lavalink server for updates and events."""
        while True:
            backoff = ExponentialBackoff()
            msg = await self.connection.receive()
            if msg.type is WSMsgType.TEXT:
                await asyncio.create_task(self.processListener(msg.json()))
            elif msg.type is WSMsgType.CLOSED:
                await asyncio.sleep(backoff.delay())

    async def processListener(self, data: Dict[str, Any]):
        """Processes data received from the Lavalink server gathered in :class:`listener()`."""
        op = data.get("op")
        if op == "playerUpdate":
            guild = self.node.bot.get_guild(int(data["guildId"]))
            player = [player for player in self.node.players if player.guild == guild][0]
            player.updateState(data)
        elif op == "stats":
            # TODO: Implement
            return
        elif op == "event":
            # TODO: Implement
            return
