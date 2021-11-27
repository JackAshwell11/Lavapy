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
import random
import string
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, Union

import aiohttp

from .exceptions import BuildTrackError, InvalidNodeSearch, LavalinkException, LoadTrackError, NodeOccupied, NoNodesConnected, WebsocketAlreadyExists
from .ext.spotify.tracks import SpotifyBase
from .stats import Stats
from .websocket import Websocket

if TYPE_CHECKING:
    import discord.ext
    from discord import VoiceRegion
    from .ext.spotify.client import SpotifyClient
    from .player import Player
    from .tracks import MultiTrack, Playable, Track

__all__ = ("NodePool",
           "Node",)

logger = logging.getLogger(__name__)


class NodePool:
    """
    Lavapy NodePool class. This holds all the :class:`Node` objects created with :meth:`createNode()`.
    """
    _nodes: Dict[str, Node] = {}

    @classmethod
    def nodes(cls) -> Dict[str, Node]:
        """Returns a mapping of identifier to node objects."""
        return cls._nodes

    @classmethod
    async def createNode(cls, *, client: Union[discord.Client, discord.AutoShardedClient, discord.ext.commands.Bot, discord.ext.commands.AutoShardedBot], host: str, port: int, password: str, region: Optional[VoiceRegion] = None, secure: bool = False, heartbeat: int = 60, spotifyClient: Optional[SpotifyClient] = None, identifier: Optional[str] = None) -> Node:
        """|coro|

        Creates a Lavapy :class:`Node` object and stores it for later use.

        Parameters
        ----------
        client: Union[:class:`discord.Client`, :class:`discord.AutoShardedClient`, :class:`discord.ext.commands.Bot`, :class:`discord.ext.commands.AutoShardedBot`]
            The client or bot object to assign to this node.
        host: str
            The IP address of the Lavalink server.
        port: int
            The port of the Lavalink server.
        password: str
            The password to the Lavalink server.
        region: Optional[:class:`discord.VoiceRegion`]
            The voice region to assign to this node.
        secure: bool
            Whether to connect securely to the Lavalink server or not.
        heartbeat: int
            How many seconds to wait before sending a ping message and waiting for a response from the Lavalink server.
        spotifyClient: Optional[SpotifyClient]
            A Lavapy Spotify client for interacting with Spotify.
        identifier: Optional[str]
            The unique identifier for this node. If not supplied, it will be generated for you.

        Raises
        ------
        NodeOccupied
            A node with the given identifier already exists.

        Returns
        -------
        Node
            A Lavapy node object.
        """
        if identifier is None:
            identifier = "".join(random.choices(string.ascii_letters + string.digits, k=8))

        if identifier in cls._nodes:
            raise NodeOccupied(f"A node with the identifier <{identifier}> already exists.")

        node = Node(client, host, port, password, region, secure, heartbeat, spotifyClient, identifier)
        cls._nodes[identifier] = node
        await node.connect()
        await node._initialiseExtensions()
        return node

    @classmethod
    def minPlayers(cls) -> Node:
        """
        An algorithm which selects the best Lavapy :class:`Node` based on the amount of players.

        Raises
        ------
        NoNodesConnected
            There are currently no nodes connected with the provided options.
        InvalidNodeSearch
            No nodes could be found with the current algorithm.

        Returns
        -------
        Node
            A Lavapy node object.
        """
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected.")
        result = sorted(cls._nodes.values(), key=lambda x: len(x.players))
        try:
            return result[0]
        except KeyError:
            raise InvalidNodeSearch("No nodes could be found using the minPlayers algorithm.")

    @classmethod
    def balanced(cls) -> Node:
        """
        An algorithm which selects the best Lavapy :class:`Node` based on each node's penalty.

        Raises
        ------
        NoNodesConnected
            There are currently no nodes connected with the provided options.
        InvalidNodeSearch
            No nodes could be found with the current algorithm.

        Returns
        -------
        Node
            A Lavapy node object.
        """
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected.")
        result = sorted(cls._nodes.values(), key=lambda x: x.penalty)
        try:
            return result[0]
        except KeyError:
            raise InvalidNodeSearch("No nodes could be found using the balanced algorithm.")

    @classmethod
    def identifier(cls, identifier: str):
        """
        An algorithm which selects the best Lavapy :class:`Node` based on its identifier.

        Raises
        ------
        NoNodesConnected
            There are currently no nodes connected with the provided options.
        InvalidNodeSearch
            No nodes could be found with the current algorithm.
        """
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected.")
        try:
            return cls._nodes[identifier]
        except KeyError:
            raise InvalidNodeSearch(f"No nodes could be found with identifier {identifier}.")

    @classmethod
    def closestNode(cls, region: VoiceRegion):
        """
        An algorithm which selects the best Lavapy :class:`Node` based on how close it is to the desired target.

        Raises
        ------
        NoNodesConnected
            There are currently no nodes connected with the provided options.
        InvalidNodeSearch
            No nodes could be found with the current algorithm.
        """
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected.")
        result = [node for node in cls._nodes.values() if node.region == region]
        try:
            return result[0]
        except KeyError:
            raise InvalidNodeSearch(f"No nodes could be found with region {region}.")

    @classmethod
    def extension(cls, extension: Type[Playable]):
        """
        An algorithm which selects the best Lavapy :class:`Node` based on the amount of players.

        Raises
        ------
        NoNodesConnected
            There are currently no nodes connected with the provided options.
        InvalidNodeSearch
            No nodes could be found with the current algorithm.
        """
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected.")
        if issubclass(extension, SpotifyBase):
            result = [node for node in cls._nodes.values() if node.spotifyClient is not None]
        else:
            result = list(cls._nodes.values())
        try:
            return result[0]
        except KeyError:
            raise InvalidNodeSearch(f"No nodes could be found with extension {extension}.")


class Node:
    """
    Lavapy Node object.

    .. warning::
        This class should not be created manually. Please use :meth:`NodePool.createNode()` instead.
    """
    def __init__(self, client: Union[discord.Client, discord.AutoShardedClient, discord.ext.commands.Bot, discord.ext.commands.AutoShardedBot], host: str, port: int, password: str, region: Optional[discord.VoiceRegion], secure: bool, heartbeat: int, spotifyClient: Optional[SpotifyClient], identifier: str) -> None:
        self._client: Union[discord.Client, discord.AutoShardedClient, discord.ext.commands.Bot, discord.ext.commands.AutoShardedBot] = client
        self._host: str = host
        self._port: int = port
        self._password: str = password
        self._region: Optional[discord.VoiceRegion] = region
        self._secure: bool = secure
        self._heartbeat: int = heartbeat
        self._spotifyClient: Optional[SpotifyClient] = spotifyClient
        self._identifier: str = identifier
        self._players: List[Player] = []
        self._stats: Optional[Stats] = None
        self._session: aiohttp.ClientSession = aiohttp.ClientSession()
        self._websocket: Optional[Websocket] = None
        self._websocketUri: str = f"{'wss' if self.secure else 'ws'}://{self.host}:{self.port}"
        self._restUri: str = f"{'https' if self._secure else 'http'}://{self.host}:{self.port}"

    def __repr__(self) -> str:
        return f"<Lavapy Node (Domain={self.host}:{self.port}) (Identifier={self.identifier}) (Region={self.region}) (Players={len(self.players)})>"

    @property
    def client(self) -> Union[discord.Client, discord.AutoShardedClient, discord.ext.commands.Bot, discord.ext.commands.AutoShardedBot]:
        """Returns the client or bot object assigned to this node."""
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
    def region(self) -> Optional[discord.VoiceRegion]:
        """Returns the voice region assigned to this node."""
        return self._region

    @property
    def secure(self) -> bool:
        """Returns whether the connection to the Lavalink server is secure or not."""
        return self._secure

    @property
    def heartbeat(self) -> int:
        """Returns the amount of seconds between ping requests."""
        return self._heartbeat

    @property
    def spotifyClient(self) -> Optional[SpotifyClient]:
        """Returns the Spotify client associated with this node if there is one."""
        return self._spotifyClient

    @property
    def identifier(self) -> str:
        """Returns the unique identifier for this node."""
        return self._identifier

    @property
    def players(self) -> List[Player]:
        """Returns a list of all Lavapy player objects which are connected to this node."""
        return self._players

    @property
    def stats(self) -> Optional[Stats]:
        """Returns useful information sent by Lavalink about this node."""
        return self._stats

    @property
    def session(self) -> aiohttp.client.ClientSession:
        """Returns the session used for sending and getting data."""
        return self._session

    @property
    def websocketUri(self) -> str:
        """Returns the URI used for initialising the websocket."""
        return self._websocketUri

    @property
    def restUri(self) -> str:
        """Returns the URI used for communicating with the Lavalink server."""
        return self._restUri

    @property
    def penalty(self) -> float:
        """Returns the load balancing penalty for this node."""
        if self.stats is None:
            return 0.0
        return self.stats.penalty.total

    async def _initialiseExtensions(self) -> None:
        """|coro|

        Initialises all the extensions linked to this :class:`Node`.
        """
        if self.spotifyClient is not None:
            logger.debug(f"Initialising spotify extension for node {self.identifier}")
            await self.spotifyClient._getBearerToken()

    async def connect(self) -> None:
        """|coro|

        Initialises the websocket connection to the Lavalink server.

        Raises
        ------
        WebsocketAlreadyExists
            The websocket for this node already exists.
        """
        logger.debug(f"Connecting to the Lavalink server at {self.host}:{self.port}")
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
        logger.debug(f"Disconnecting node {self.identifier}")
        for player in self.players:
            await player.disconnect(force=force)

        try:
            await self._websocket.disconnect()
            del NodePool._nodes[self.identifier]
        except Exception as e:
            logger.debug(f"Failed to remove node {self.identifier} with error {e}")

    async def _getData(self, endpoint: str, params: Dict[str, str]) -> Tuple[Dict[str, Any], aiohttp.ClientResponse]:
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
            A tuple containing the response from Lavalink as well as the websocket response to determine the status of the request.
        """
        logger.debug(f"Getting endpoint {endpoint} with data {params}")
        headers = {
            "Authorization": self.password
        }
        async with await self.session.get(f"{self.restUri}/{endpoint}", headers=headers, params=params) as req:
            data = await req.json()
        return data, req

    async def _send(self, payload: Dict[str, Any]) -> None:
        """|coro|

        Send a payload to Lavalink without a response.

        Parameters
        ----------
        payload: Dict[str, Any]
            The payload to send to Lavalink.
        """
        logger.debug(f"Sending payload {payload}")
        await self._websocket.connection.send_json(payload)

    async def buildTrack(self, cls: Type[Track], id: str) -> Track:
        """|coro|

        Builds a :class:`Track` from a base64 track ID.

        Parameters
        ----------
        cls: Type[Track]
            The Lavapy resource to return an instance of
        id: str
            The base64 track ID.

        Raises
        ------
        BuildTrackError
            An error occurred while building the track.

        Returns
        -------
        Track
            A Lavapy track object.
        """
        logger.debug(f"Building track with cls {cls} and id {id}")
        track, response = await self._getData("decodetrack", {"track": id})
        if response.status != 200:
            raise BuildTrackError("A error occurred while building the track.", track)
        return cls(id, track)

    async def getTracks(self, cls: Type[Playable], query: str) -> Optional[Union[Track, List[Track], MultiTrack]]:
        """|coro|

        Gets data about a :class:`Track` or :class:`MultiTrack` from Lavalink.

        Parameters
        ----------
        cls: Type[Playable]
            The Lavapy resource to create an instance of.
        query: str
            The query to search for via Lavalink.

        Returns
        -------
        Optional[Union[Track, List[Track], MultiTrack]]
            A Lavapy resource which can be used to play music.
        """
        logger.info(f"Getting data with cls {cls} and query: {query}")
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
            # noinspection PyTypeChecker
            return cls(trackInfo["track"], trackInfo["info"])
        elif loadType == "SEARCH_RESULT":
            # noinspection PyTypeChecker
            return [cls(element["track"], element["info"]) for element in data["tracks"]]
        elif loadType == "PLAYLIST_LOADED":
            playlistInfo = data["playlistInfo"]
            # noinspection PyTypeChecker
            return cls(playlistInfo["name"], [cls._trackCls(track["track"], track["info"]) for track in data["tracks"]])
