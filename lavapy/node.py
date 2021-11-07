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

import logging
from typing import Optional, List, Dict, Any, Tuple, TYPE_CHECKING
import aiohttp
from aiohttp import ClientResponse

from discord.enums import VoiceRegion

from .exceptions import WebsocketAlreadyExists, BuildTrackError
from .websocket import Websocket
from .tracks import Track
from .utils import ClientType

if TYPE_CHECKING:
    from .player import Player
    from .utils import Stats

__all__ = ("Node",)

logger = logging.getLogger(__name__)


class Node:
    """
    Lavapy Node object.

    .. warning::
        This class should not be created manually. Please use :meth:`NodePool.create_node()` instead.
    """
    def __init__(self, client: ClientType, host: str, port: int, password: str, region: Optional[VoiceRegion], identifier: str) -> None:
        self._client: ClientType = client
        self._host: str = host
        self._port: int = port
        self._password: str = password
        self._region: Optional[VoiceRegion] = region
        self._identifier: str = identifier
        self._players: List[Player] = []
        self._stats: Optional[Stats] = None
        self._session: aiohttp.ClientSession = aiohttp.ClientSession()
        self._websocket: Optional[Websocket] = None

    def __repr__(self) -> str:
        return f"<Lavapy Node (Domain={self.host}:{self.port}) (Identifier={self.identifier}) (Region={self.region}) (Players={len(self.players)})>"

    @property
    def client(self) -> ClientType:
        """Returns the :class:`discord.Client`, :class:`discord.AutoShardedClient`, :class:`discord.ext.commands.Bot` or :class:`discord.ext.commands.AutoShardedBot` which is assigned to this node."""
        return self._client

    @property
    def host(self) -> str:
        """Returns the IP address of the Lavalink server."""
        return self._host

    @property
    def port(self) -> int:
        """Returns the port of the Lavalink server."""
        return self._port

    @property
    def password(self) -> str:
        """Returns the password to the Lavalink server."""
        return self._password

    @property
    def region(self) -> VoiceRegion:
        """Returns the :class:`discord.VoiceRegion` assigned to this node."""
        return self._region

    @property
    def identifier(self) -> str:
        """Returns the unique identifier for this node."""
        return self._identifier

    @property
    def players(self) -> List[Player]:
        """Returns a list containing all Lavapy :class:`Player`s which are connected to this node."""
        return self._players

    @property
    def stats(self) -> Optional[Stats]:
        """Returns useful information sent by Lavalink about this node."""
        return self._stats

    @stats.setter
    def stats(self, newStats: Stats) -> None:
        """Sets the value of :class:`Stats`."""
        self._stats = newStats

    @property
    def session(self) -> aiohttp.ClientSession:
        """Returns the :class:`aiohttp.ClientSession` used for sending and getting data."""
        return self._session

    async def connect(self) -> None:
        """|coro|

        Initialise the websocket to the Lavalink server.

        Raises
        ------
        WebsocketAlreadyExists
            The websocket for this :class:`Node` already exists.
        """
        logger.debug(f"Connecting to the Lavalink server at: {self.host}:{self.port}")
        if self._websocket is None:
            self._websocket = Websocket(self)
        else:
            raise WebsocketAlreadyExists("Websocket already initialised.")

    async def disconnect(self, *, force: bool = False) -> None:
        """|coro|

        Disconnects this :class:`Node` and removes it from the :class:`NodePool`.

        Parameters
        ----------
        force: bool
            Whether to force the disconnection. This is currently not used.
        """
        for player in self.players:
            await player.disconnect(force=force)

        self._websocket.listener.cancel()
        await self._websocket.connection.close()

    async def _getData(self, dest: str, params: Optional[Dict[str, str]]) -> Tuple[Dict[str, Any], ClientResponse]:
        """|coro|

        Make a request to Lavalink with a given query and return a response.

        Parameters
        ----------
        dest: str
            The request to send to Lavalink and get a response for.
        params: Dict[str, str]
            A dict containing additional info to send to Lavalink.

        Returns
        -------
        Tuple[Dict[str, Any], :class:aiohttp.ClientResponse`]
            A tuple containing the response from Lavalink as well as a :class:aiohttp.ClientResponse` object to determine the status of the request.
        """
        logger.debug(f"Getting data with destination: {dest}")
        headers = {
            "Authorization": self.password
        }
        async with await self.session.get(dest, headers=headers, params=params) as req:
            data = await req.json()
        return data, req

    async def send(self, payload: Dict[str, Any]) -> None:
        """|coro|

        Send a payload to Lavalink without a response.

        Parameters
        ----------
        payload: Dict[str, Any]
            The payload to send to Lavalink.
        """
        logger.debug(f"Sending payload: {payload}")
        await self._websocket.connection.send_json(payload)

    async def buildTrack(self, id: str) -> Track:
        """|coro|

        Builds a :class:`Track` from a base64 ID.

        Parameters
        ----------
        id: str
            The base64 ID.

        Raises
        ------
        BuildTrackError
            An error occurred while building the :class:`Track`.

        Returns
        -------
        Track
            A Lavapy :class:`Track` object.
        """
        payload = {
            "track": id
        }
        track, response = await self._getData(f"http://{self.host}:{self.port}/decodetrack?track=", payload)
        if response.status != 200:
            raise BuildTrackError("A error occurred while building the track.", track)
        return Track(id, track)
