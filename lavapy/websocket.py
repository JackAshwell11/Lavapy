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
from typing import TYPE_CHECKING, Any, Dict, Optional

import aiohttp

from .backoff import ExponentialBackoff
from .events import LavapyEvent, TrackEndEvent, TrackExceptionEvent, TrackStartEvent, TrackStuckEvent, WebsocketClosedEvent, WebsocketOpenEvent
from .stats import Stats
from .tracks import Track

if TYPE_CHECKING:
    from .player import Player
    from .pool import Node

logger = logging.getLogger(__name__)

__all__ = ("Websocket",)


class Websocket:
    """
    Lavapy Websocket object.

    Parameters
    ----------
    node: Node
        The Lavapy node object which manages this websocket.
    """
    def __init__(self, node: Node) -> None:
        self._node: Node = node
        self._connection: Optional[aiohttp.client.ClientWebSocketResponse] = None
        self._listener: Optional[asyncio.Task] = None
        asyncio.create_task(self.connect())

    def __repr__(self) -> str:
        return f"<Lavapy Websocket (Domain={self.node.host}:{self.node.port}) (Connected={self.connected})>"

    @property
    def node(self) -> Node:
        """Returns the Lavapy node which manages this websocket."""
        return self._node

    @property
    def connected(self) -> bool:
        """Returns whether the websocket is connected or not."""
        return self._connection is not None and not self.connection.closed

    @property
    def connection(self) -> Optional[aiohttp.client.ClientWebSocketResponse]:
        """Returns the websocket connection."""
        return self._connection

    @property
    def listener(self) -> Optional[asyncio.Task]:
        """Returns the task which pings the Lavalink server for updates."""
        return self._listener

    def getPlayer(self, guildID: int) -> Player:
        """
        Returns a Lavapy :class:`Player` object based on a specific :class:`discord.Guild` ID.

        Parameters
        ----------
        guildID: int
            The guild ID to get a Lavapy player object for.

        Returns
        -------
        Player
            A Lavapy player object.
        """
        return [player for player in self.node.players if player.guild.id == guildID][0]

    async def connect(self) -> None:
        """|coro|

        Establishes the connection to the Lavalink server.

        Raises
        ------
        aiohttp.client.ClientConnectorError
            The domain name is invalid.
        """
        headers = {
            "Authorization": self.node.password,
            "User-Id": str(self.node.client.user.id),
            "Client-Name": "Lavapy"
        }
        logger.debug(f"Attempting connection with for node {self.node.identifier}")
        try:
            self._connection = await self.node.session.ws_connect(self.node.websocketUri, headers=headers, heartbeat=self.node.heartbeat)
        except Exception as error:
            if isinstance(error, aiohttp.WSServerHandshakeError) and error.status == 401:
                logger.error(f"Authorisation failed for node {self.node.identifier}")
            else:
                logger.error(f"Connection failure for node {self.node.identifier} with error {error}")
            return
        self._listener = self.node.client.loop.create_task(self.createListener())
        logger.debug(f"Connection established for node {self.node.identifier}")
        event = WebsocketOpenEvent(self.node)
        await self.dispatchEvent(f"lavapy_{event.event}", event.payload)

    async def disconnect(self) -> None:
        """|coro|

        Closes the connection to the Lavalink server.
        """
        logger.debug(f"Closing connection for node {self.node.identifier}")
        self.listener.cancel()
        await self.connection.close()

    async def createListener(self) -> None:
        """|coro|

        Continuously pings the Lavalink server for updates and events.
        """
        backoff = ExponentialBackoff()
        while True:
            msg = await self.connection.receive()
            if msg.type is aiohttp.WSMsgType.CLOSED:
                logger.debug(f"Websocket closed for node {self.node.identifier} with info {msg.extra}")
                retry = backoff.delay()
                logger.debug(f"Retrying connection in {retry} seconds")
                await asyncio.sleep(retry)
            else:
                if msg.data == 1011:
                    logger.error(f"Internal Lavalink error encountered with node {self.node.identifier}. Terminating without retries. Consider updating your Lavalink server.")
                    self.listener.cancel()
                asyncio.create_task(self.processListener(msg.json()))

    async def processListener(self, data: Dict[str, Any]) -> None:
        """|coro|

        Processes data received from the Lavalink server gathered in :meth:`createListener()`.

        Parameters
        ----------
        data: Dict[str, Any]
            The raw data received from Lavalink.
        """
        op = data.get("op")
        if op == "playerUpdate":
            try:
                player = self.getPlayer(int(data["guildId"]))
                player._updateState(data)
            except IndexError:
                # Player has recently sent a destroy op so don't update state
                pass
        elif op == "event":
            event = await self.getEventPayload(data["type"], data)
            await self.dispatchEvent(f"lavapy_{event.event}", event.payload)
        elif op == "stats":
            self.node._stats = Stats(self.node, data)

    async def getEventPayload(self, name: str, data: Dict[str, Any]) -> LavapyEvent:
        """|coro|

        Processes events received from Lavalink sent from :meth:`processListener()`.

        Parameters
        ----------
        name: str
            The event name.
        data: Dict[str, Any]
            The event payload sent by Lavalink.

        Returns
        -------
        LavapyEvent
            The LavapyEvent object which corresponds to the event payload.
        """
        logger.debug(f"Received event payload {data}")
        if name == "WebSocketClosedEvent":
            return WebsocketClosedEvent(self.node, data)

        player = self.getPlayer(int(data["guildId"]))
        track = await self.node.buildTrack(Track, data["track"])
        if name == "TrackStartEvent":
            return TrackStartEvent(player, track)
        elif name == "TrackEndEvent":
            if player.isRepeating:
                await player.play(player.track)
            elif data["reason"] == "FINISHED":
                player._track = None
            return TrackEndEvent(player, track, data)
        elif name == "TrackExceptionEvent":
            return TrackExceptionEvent(player, track, data)
        elif name == "TrackStuckEvent":
            return TrackStuckEvent(player, track, data)

    async def dispatchEvent(self, event: str, payload: Dict[str, Any]) -> None:
        """|coro|

        Dispatches events to Discord.

        Parameters
        ----------
        event: str
            The event name.
        payload: Dict[str, Any]
            The payload to dispatch with the event. This is sent to `**kwargs`.
        """
        logger.debug(f"Dispatching event {event} with payload {payload}")
        self.node.client.dispatch(event, **payload)
