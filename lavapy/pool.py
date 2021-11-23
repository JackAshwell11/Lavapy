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

import string
import logging
import random
from enum import Enum
from typing import TYPE_CHECKING, Optional,  Union, Dict, List, Tuple, Any, Type

import aiohttp
import discord.ext
from aiohttp import ClientResponse

from .tracks import Track
from .websocket import Websocket
from .exceptions import WebsocketAlreadyExists, NoNodesConnected, InvalidIdentifier, NodeOccupied, BuildTrackError, LavalinkException, LoadTrackError
from .ext.spotify.client import SpotifyClient
from .ext.spotify.exceptions import InvalidSpotifyClient

if TYPE_CHECKING:
    from discord import VoiceRegion
    from .player import Player
    from .utils import Stats
    from .tracks import Playable, MultiTrack

__all__ = ("NodeAlgorithmsType",
           "NodePool",
           "Node")

logger = logging.getLogger(__name__)


class NodeAlgorithmsType(Enum):
    minPlayers = 0
    balanced = 1
    identifier = 2
    closestNode = 3
    extension = 4


class NodePool:
    """
    Lavapy NodePool class. This holds all the :class:`Node` objects created with :meth:`createNode()`.
    """
    _nodes: Dict[str, Node] = {}

    @classmethod
    def getNode(cls, algorithm: NodeAlgorithmsType, identifier: Optional[str] = None, region: Optional[VoiceRegion] = None, extension: Type[Playable] = None) -> Node:
        """
        Retrieves a :class:`Node` object based on identifier, :class:`discord.VoiceRegion` or neither (randomly).

        Parameters
        ----------
        algorithm: NodeAlgorithmsType
            The desired algorithm to use.
        identifier: Optional[str]
            The unique identifier for the desired node.
        region: Optional[:class:`discord.VoiceRegion`]
            The voice region a specific node is assigned to.
        extension: Type[Playable]
            The extension to find a node which supports it.

        Returns
        -------
        Node
            A Lavapy node object.
        """
        if algorithm is NodeAlgorithmsType.minPlayers:
            return cls._minPlayers()
        if algorithm is NodeAlgorithmsType.balanced:
            return cls._balanced()
        elif algorithm is NodeAlgorithmsType.identifier:
            return cls._identifier(identifier)
        elif algorithm is NodeAlgorithmsType.closestNode:
            return cls._closestNode(region)
        elif algorithm is NodeAlgorithmsType.extension:
            return cls._extension(extension)

    @classmethod
    async def createNode(cls, client: Union[discord.Client, discord.AutoShardedClient, discord.ext.commands.Bot, discord.ext.commands.AutoShardedBot], host: str, port: int, password: str, region: Optional[VoiceRegion] = None, secure: bool = False, spotifyClient: Optional[SpotifyClient] = None, identifier: Optional[str] = None) -> Node:
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
        Node:
            A Lavapy node object.
        """
        if identifier is None:
            identifier = "".join(random.choices(string.ascii_letters + string.digits, k=8))

        if identifier in cls._nodes:
            raise NodeOccupied(f"A node with the identifier <{identifier}> already exists.")

        node = Node(client, host, port, password, region, secure, spotifyClient, identifier)
        cls._nodes[identifier] = node
        await node.connect()
        await node._initialiseExtensions()
        return node

    @classmethod
    def _minPlayers(cls) -> Node:
        """
        An algorithm which selects the best Lavapy :class:`Node` based on the amount of players.

        Raises
        ------
        NoNodesConnected
            There are currently no nodes connected with the provided options.

        Returns
        -------
        Node
            A Lavapy node object.
        """
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected.")
        return sorted(cls._nodes.values(), key=lambda x: len(x.players))[0]

    @classmethod
    def _balanced(cls) -> Node:
        """
        An algorithm which selects the best Lavapy :class:`Node` based on each node's penalty.

        Raises
        ------
        NoNodesConnected
            There are currently no nodes connected with the provided options.

        Returns
        -------
        Node
            A Lavapy node object.
        """
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected.")
        return sorted(cls._nodes.values(), key=lambda x: x.penalty)[0]

    @classmethod
    def _identifier(cls, identifier: str):
        """
        An algorithm which selects the best Lavapy :class:`Node` based on its identifier.

        Raises
        ------
        NoNodesConnected
            There are currently no nodes connected with the provided options.
        InvalidIdentifier
            A node does not exist with that identifier.
        """
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected.")
        try:
            return cls._nodes[identifier]
        except KeyError:
            raise InvalidIdentifier(f"No nodes exist with the identifier {identifier}")

    @classmethod
    def _closestNode(cls, region: VoiceRegion):
        """
        An algorithm which selects the best Lavapy :class:`Node` based on how close it is to the desired target.

        Raises
        ------
        NoNodesConnected
            There are currently no nodes connected with the provided options.
        """
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected.")

    @classmethod
    def _extension(cls, extension: Type[Playable]):
        """
        An algorithm which selects the best Lavapy :class:`Node` based on the amount of players.

        Raises
        ------
        NoNodesConnected
            There are currently no nodes connected with the provided options.
        """
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected.")


class Node:
    """
    Lavapy Node object.

    .. warning::
        This class should not be created manually. Please use :meth:`NodePool.createNode()` instead.
    """
    def __init__(self, client: Union[discord.Client, discord.AutoShardedClient, discord.ext.commands.Bot, discord.ext.commands.AutoShardedBot], host: str, port: int, password: str, region: Optional[discord.VoiceRegion], secure: bool, spotifyClient: Optional[SpotifyClient], identifier: str) -> None:
        self._client: Union[discord.Client, discord.AutoShardedClient, discord.ext.commands.Bot, discord.ext.commands.AutoShardedBot] = client
        self._host: str = host
        self._port: int = port
        self._password: str = password
        self._region: Optional[discord.VoiceRegion] = region
        self._secure: bool = secure
        if spotifyClient is not None:
            if isinstance(spotifyClient, SpotifyClient):
                self._spotifyClient: SpotifyClient = spotifyClient
            else:
                raise InvalidSpotifyClient(f"Invalid Spotify client for node {self.identifier}")
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
    def region(self) -> discord.VoiceRegion:
        """Returns the voice region assigned to this node."""
        return self._region

    @property
    def secure(self) -> bool:
        """Returns whether the connection to the Lavalink server is secure or not."""
        return self._secure

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
        await self.spotifyClient._getBearerToken()

    async def connect(self) -> None:
        """|coro|

        Initialises the websocket connection to the Lavalink server.

        Raises
        ------
        WebsocketAlreadyExists
            The websocket for this node already exists.
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

        try:
            self._websocket.listener.cancel()
            await self._websocket.connection.close()
            del NodePool._nodes[self.identifier]
        except Exception as e:
            logger.debug(f"Failed to remove node {self.identifier} with error {e}")

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
        logger.debug(f"Sending payload: {payload}")
        await self._websocket.connection.send_json(payload)

    async def buildTrack(self, id: str) -> Track:
        """|coro|

        Builds a :class:`Track` from a base64 track ID.

        Parameters
        ----------
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
        track, response = await self._getData("decodetrack", {"track": id})
        if response.status != 200:
            raise BuildTrackError("A error occurred while building the track.", track)
        return Track(id, track)

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
        logger.info(f"Getting data with query: {query}")
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
