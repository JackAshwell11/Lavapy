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
from typing import Union, Optional, List, Dict, Any, Tuple, TYPE_CHECKING
import aiohttp
from aiohttp import ClientResponse

from discord.enums import VoiceRegion
from discord.ext.commands import Bot, AutoShardedBot

from .exceptions import WebsocketAlreadyExists, BuildTrackError
from .websocket import Websocket
from .tracks import Track

if TYPE_CHECKING:
    from .player import Player

__all__ = ("Node",)

logger = logging.getLogger(__name__)


class Node:
    """
    Lavapy Node object.

    .. warning::
        This class should not be created manually. Please use :meth:`NodePool.create_node()` instead.

    Attributes
    ----------
    bot: Union[:class:`discord.ext.commands.Bot`, :class:`discord.ext.commands.AutoShardedBot`]
        The discord.py Bot or AutoShardedBot object.
    host: str
        The IP address of the Lavalink server.
    port: int
        The port of the Lavalink server.
    password: str
        The password to the Lavalink server.
    region: Optional[:class:`discord.VoiceRegion`]
        The discord.py VoiceRegion to assign to this node.
    identifier: str
        The unique identifier for this node.
    session: aiohttp.ClientSession
        The aiohttp session used for sending and getting data.
    players: List[Player]
        A list containing all Lavapy Players which are connected to this node.
    """
    def __init__(self, bot: Union[Bot, AutoShardedBot], host: str, port: int, password: str, region: Optional[VoiceRegion], identifier: str) -> None:
        self.bot: Union[Bot, AutoShardedBot] = bot
        self.host: str = host
        self.port: int = port
        self.password: str = password
        self.region: Optional[VoiceRegion] = region
        self.identifier: str = identifier
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.players: List[Player] = []
        self._websocket: Optional[Websocket] = None

    def __repr__(self) -> str:
        return f"<Lavapy Node (Domain={self.host}:{self.port}) (Identifier={self.identifier}) (Region={self.region}) (Players={len(self.players)})>"

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
            raise WebsocketAlreadyExists("Websocket already initialised")

    async def getData(self, dest: str, params: Optional[Dict[str, str]]) -> Tuple[Dict[str, Any], ClientResponse]:
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
        Tuple[Dict[str, Any], ClientResponse]
            A tuple containing the response from Lavalink as well as a ClientResponse object to determine the status of the request.
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

        Builds a track from a base64 :class:`Track` ID.

        Parameters
        ----------
        id: str
            The base 64 track ID.

        Returns
        -------
        Track
            A Lavapy Track object.
        """
        payload = {
            "track": id
        }
        track, response = await self.getData(f"http://{self.host}:{self.port}/decodetrack?track=", payload)
        if response.status != 200:
            raise BuildTrackError
        return Track(id, track)
