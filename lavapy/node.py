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
from typing import TYPE_CHECKING, Optional, Union, Tuple, List, Dict, Type, Any
import aiohttp
from aiohttp import ClientResponse

from discord.enums import VoiceRegion

from .exceptions import WebsocketAlreadyExists, BuildTrackError, LavalinkException, LoadTrackError
from .websocket import Websocket
from .tracks import Track, MultiTrack
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
        """Returns a list of all Lavapy :class:`Player` objects which are connected to this node."""
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

    async def _getData(self, endpoint: str, params: Dict[str, str]) -> Tuple[Dict[str, Any], ClientResponse]:
        """|coro|

        Make a request to Lavalink with a given endpoint and return a response.

        Parameters
        ----------
        endpoint: str
            The endpoint to query from Lavalink.
        params: Dict[str, str]
            A dict containing additional info to send to Lavalink.

        Returns
        -------
        Tuple[Dict[str, Any], :class:`aiohttp.ClientResponse`]
            A tuple containing the response from Lavalink as well as a :class:aiohttp.ClientResponse` object to determine the status of the request.
        """
        logger.debug(f"Getting endpoint {endpoint} with data {params}")
        headers = {
            "Authorization": self.password
        }
        async with await self.session.get(f"http://{self.host}:{self.port}/{endpoint}", headers=headers, params=params) as req:
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
        track, response = await self._getData("decodetrack", {"track": id})
        if response.status != 200:
            raise BuildTrackError("A error occurred while building the track.", track)
        return Track(id, track)

    async def getTracks(self, cls: Union[Type[Track], Type[MultiTrack]], query: str) -> Optional[Union[Track, List[Track], MultiTrack]]:
        """|coro|

        Gets data about a :class:`Track` from Lavalink.

        Parameters
        ----------
        cls: Union[Track, MultiTrack]
            The Lavapy resource to create an instance of.
        query: str
            The query to search for via Lavalink.

        Returns
        -------
        Optional[Union[Track, List[Track]]]
            A Lavapy resource which can be used to play music.
        """
        data, response = await self._getData("loadtracks", {"identifier": query})
        if response.status != 200:
            raise LavalinkException("Invalid response from lavalink.")

        loadType = data.get("loadType")
        if loadType == "LOAD_FAILED":
            raise LoadTrackError(f"Track failed to load with data: {data}.")
        elif loadType == "NO_MATCHES":
            return None
        elif loadType == "TRACK_LOADED":
            trackInfo = data["tracks"][0]
            return cls(trackInfo["track"], trackInfo["info"])
        elif loadType == "SEARCH_RESULT":
            return [cls(element["track"], element["info"]) for element in data["tracks"]]
        elif loadType == "PLAYLIST_LOADED":
            playlistInfo = data["playlistInfo"]
            return cls(playlistInfo["name"], playlistInfo["selectedTrack"], [cls._trackCls(track["track"], track["info"]) for track in data["tracks"]])
