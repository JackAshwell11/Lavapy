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
from typing import Dict, Any, List, Union, Optional, TYPE_CHECKING
from urllib.parse import quote

from .exceptions import LavalinkException, LoadTrackError

if TYPE_CHECKING:
    from .node import Node

__all__ = ("Playable",
           "Track",
           "Playlist",
           "SoundcloudTrack",
           "YoutubeTrack",
           "YoutubeMusicTrack",
           "YoutubePlaylist",)

logger = logging.getLogger(__name__)


class Playable:
    """The base class for all Lavapy playable objects."""

    def __repr__(self) -> str:
        return f"<Lavapy Playable>"

    @staticmethod
    def checkNode(node) -> Node:
        """
        Checks if a :class:`Node` is valid. If not, it will pick a random one from the :class:`NodePool`.

        Parameters
        ----------
        node: Node
            The Node to check.

        Returns
        -------
        Node
            A valid Node object.
        """
        if node is None:
            # Avoid a circular dependency with node.buildTrack()
            from .pool import NodePool
            node = NodePool.getNode()
        return node

    @staticmethod
    async def getInfo(cls, node: Node, dest: str, params: Optional[Dict[str, str]]) -> Optional[Union[YoutubePlaylist, Track, List[Track]]]:
        """|coro|

        Actual function which gets and processes the track or playlist info received from Lavalink.

        Parameters
        ----------
        cls
            The class to return an instance of.
        node: Node
            The Node to use for searching.
        dest: str
            The request to send to Lavalink and get a response for.
        params: Optional[Dict[str, str]]
            A dict containing additional info to send to Lavalink.

        Raises
        ------
        LavalinkException
            Lavalink returned an invalid response.

        Returns
        -------
        Optional[Union[YoutubePlaylist, Track, List[Track]]]
            A YoutubePlaylist object, an individual Track object or a list of Track objects.
        """
        data, response = await node.getData(dest, params)
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
            return cls(playlistInfo["name"], playlistInfo["selectedTrack"], data["tracks"])

    @classmethod
    async def identifier(cls, node: Optional[Node], identifier: str) -> Optional[Playable]:
        """|coro|

        Gets a :class:`YoutubeTrack` or :class:`YoutubePlaylist` from Youtube based on a given identifier. This will return only one result if the identifier leads to a track.

        Parameters
        ----------
        node: Optional[Node]
            The :class:`Node` to use for searching.
        identifier:
            The identifier of the track or playlist.

        Returns
        -------
        Optional[Union[YoutubeTrack, YoutubePlaylist]]
            A YoutubeTrack object or a YoutubePlaylist object.
        """
        node = cls.checkNode(node)
        logger.info(f"Getting {cls} with identifier: {identifier}")
        return await cls.getInfo(cls, node, f"http://{node.host}:{node.port}/loadtracks", {"identifier": identifier})


class Track(Playable):
    """
    The base class for all Lavapy track objects.

    Attributes
    ----------
    id: str
        The unique base64 track ID which can be used to rebuild a track.
    info: Dict[str, Any]
        The raw track info.
    identifier: str
        The track's unique identifier.
    isSeekable: bool
        A bool stating if a track can be seeked or not.
    author: str
        The author of the track.
    length: int
        The duration of the track in seconds.
    isStream: bool
        A bool stating if a track is a stream or not.
    type: str
        The source site of the track.
    title: str
        The title of the track.
    uri: str
        The track's URI.
    """
    def __init__(self, id: str, info: Dict[str, Any]) -> None:
        self.id: str = id
        self.info: Dict[str, Any] = info
        self.identifier: str = info["identifier"]
        self.isSeekable: bool = info["isSeekable"]
        self.author: str = info["author"]
        self.length: int = info["length"]
        self.isStream: bool = info["isStream"]
        self.type: str = info["sourceName"]
        self.title: str = info["title"]
        self.uri: str = info["uri"]

    def __repr__(self) -> str:
        return f"<Lavapy Track (Identifier={self.identifier}) (Type={self.type})>"

    @classmethod
    async def query(cls, query: str, node: Optional[Node] = None, returnFirst: bool = True) -> Optional[Union[Track, List[Track]]]:
        """
        Gets an :class:`Track` based on a given query. This will return multiple search results.

        Parameters
        ----------
        query: str
            A Youtube query to search for. This will return multiple tracks.
        node: Optional[Node]
            The :class:`Node` to use for searching.
        returnFirst: bool
            Whether to return only the first result or not. By default, this is True

        Returns
        -------
        Optional[Union[Track, List[Track]]]
            An individual Track object or a list of Track objects.
        """
        node = cls.checkNode(node)
        logger.info(f"Getting {cls} with query: {query}")
        tracks = await cls.getInfo(cls, node, f"http://{node.host}:{node.port}/loadtracks?identifier={cls._searchType}{quote(query)}", None)
        if tracks is not None:
            if returnFirst:
                return tracks[0]
            else:
                return tracks


class Playlist(Playable):
    """Base class for all Lavapy playlists. This is just here as a placeholder for future upgrades."""

    def __repr__(self):
        return f"<Lavapy Playlist>"


class SoundcloudTrack(Track):
    """A track created using a search to Soundcloud."""

    _searchType: str = "scsearch:"

    def __repr__(self):
        return f"<Lavapy SoundcloudTrack (Identifier={self.identifier})>"

    @classmethod
    async def identifier(cls, node: Optional[Node], identifier: str) -> Optional[Playable]:
        """DO NOT USE THIS METHOD SINCE SOUNDCLOUD IDENTIFIERS ARE BROKEN."""
        raise NotImplementedError("Currently Soundcloud identifiers can't be gotten, so this function is useless.")


class YoutubeTrack(Track):
    """A track created using a search to Youtube."""

    _searchType: str = "ytsearch:"

    def __repr__(self):
        return f"<Lavapy YoutubeTrack (Identifier={self.identifier})>"


class YoutubeMusicTrack(Track):
    """A track created using a search to Youtube Music."""

    _searchType: str = "ytmsearch:"

    def __repr__(self):
        return f"<Lavapy YoutubeMusicTrack (Identifier={self.identifier})>"


class YoutubePlaylist(Playlist):
    """
    A Lavapy YoutubePlaylist object.

    Attributes
    ----------
    name: str
        The playlist's name.
    selectedTrack: int
        The currently selected track to play.
    trackArr: List[Dict[str, Any]]
        A list of dicts containing raw track info.
    """
    def __init__(self, name: str, selectedTrack: int, trackArr: List[Dict[str, Any]]):
        self.name: str = name
        self.selectedTrack: int = selectedTrack
        self.tracks: List[Track] = [YoutubeTrack(track["track"], track["info"]) for track in trackArr]

    def __repr__(self):
        return f"<Lavapy YoutubePlaylist (Name={self.name}) (Track count={len(self.tracks)})>"
