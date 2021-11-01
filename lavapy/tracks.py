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

__all__ = ("Track",
           "Playlist",
           "Searcher",)

logger = logging.getLogger(__name__)


class Track:
    """
    A Lavapy Track object. This should not be created manually, instead use the player object to get tracks

    Parameters
    ----------
    id: str
        The unique base64 track ID which can be used to rebuild a track
    info: Dict[str, Any]
        The raw track info

    Attributes
    ----------
    id: str
        The unique base64 track ID which can be used to rebuild a track
    info: Dict[str, Any]
        The raw track info
    identifier: str
        The track's unique identifier
    isSeekable: bool
        A bool stating if a track can be seeked or not
    author: str
        The author of the track
    length: int
        The duration of the track in seconds
    type: str
        The source site of the track
    title: str
        The title of the track
    uri: str
        The track's URI
    """
    def __init__(self, id: str, info: Dict[str, Any]) -> None:
        self.id: str = id
        self.info: Dict[str, Any] = info
        self.identifier: str = info.get("identifier")
        self.isSeekable: bool = info.get("isSeekable")
        self.author: str = info.get("author")
        self.length: int = info.get("length")
        self.type: str = info.get("sourceName")
        self.title: str = info.get("title")
        self.uri: str = info.get("uri")

    def __repr__(self) -> str:
        return f"<Lavapy Track (Identifier={self.identifier}) (Type={self.type})>"


class Playlist:
    """
    A Lavapy Playlist object. This should not be created manually, instead use the player object to get playlists

    Parameters
    ----------
    name: str
        The playlist's name
    selectedTrack: int
        The currently selected track to play
    trackArr: List[Dict[str, Any]]
        A list of dicts containing raw track info

    Attributes
    ----------
    name: str
        The playlist's name
    selectedTrack: int
        The currently selected track to play
    trackArr: List[Dict[str, Any]]
        A list of dicts containing raw track info
    """
    def __init__(self, name: str, selectedTrack: int, trackArr: List[Dict[str, Any]]):
        self.name: str = name
        self.selectedTrack = selectedTrack
        self.tracks: List[Track] = [Track(track["track"], track["info"]) for track in trackArr]

    def __repr__(self):
        return f"<Lavapy Playlist (Name={self.name}) (Track count={len(self.tracks)})>"


class Searcher:
    """
    A class which abstracts away most of the logic involved with getting and processing track and playlist info

    This is automatically created when a node is initialised so can be accessed through the player object:

    .. code::
        trackQuery: lavapy.Track = await player.searcher.youtubeTrack(query="Rick Astley - Never Gonna Give You Up")
        trackIdentifier: lavapy.Track = await player.searcher.youtubeTrack(identifier="dQw4w9WgXcQ")
        playlist: lavapy.Playlist = await player.searcher.youtubePlaylist("PLMC9KNkIncKseYxDN2niH6glGRWKsLtde")

    Parameters
    ----------
    node: Node
        The Lavapy Node object which is used for getting track and playlist info

    Attributes
    ----------
    node: Node
        The Lavapy Node object which is used for getting track and playlist info
    """
    def __init__(self, node: Node):
        self.node = node

    async def youtubeTrack(self, query: str = None, identifier: str = None, returnFirst: bool = True) -> Optional[Union[Track, List[Track]]]:
        """
        Gets a youtube track based on either a query (multiple search results) or an identifier (one result)

        Parameters
        ----------
        query: str
            A youtube query to search for. This will return multiple tracks
        identifier str
            The identifier of the youtube song. This will only return one track
        returnFirst: bool
            Whether to return only the first result or not. By default, this is True
        """
        if query is not None:
            logger.info(f"Getting Youtube tracks with query: {query}")
            query = f"ytsearch:{query}"
            return await self._getTracks(f"http://{self.node.host}:{self.node.port}/loadtracks?identifier={quote(query)}", None, returnFirst)
        elif identifier is not None:
            logger.info(f"Getting Youtube track with identifier: {identifier}")
            return await self._getTracks(f"http://{self.node.host}:{self.node.port}/loadtracks", {"identifier": identifier}, returnFirst)

    async def youtubePlaylist(self, identifier: str) -> Optional[Playlist]:
        """
        Gets a youtube playlist based on a given identifier

        Parameters
        ----------
        identifier: str
            The identifier of the youtube playlist
        """
        return await self._getPlaylist(f"http://{self.node.host}:{self.node.port}/loadtracks", {"identifier": identifier})

    async def soundcloudTrack(self, query: str = None, identifier: str = None, returnFirst: bool = True) -> Optional[Union[Track, List[Track]]]:
        """
        Gets a soundcloud track based on either a query (multiple search results) or an identifier (one result)

        Parameters
        ----------
        query: str
            A soundcloud query to search for. This will return multiple tracks
        identifier str
            The identifier of the soundcloud song. This will only return one track
        returnFirst: bool
            Whether to return only the first result or not. By default, this is True
        """
        if query is not None:
            query = f"scsearch:{query}"
            return await self._getTracks(f"http://{self.node.host}:{self.node.port}/loadtracks?identifier={quote(query)}", None, returnFirst)
        elif identifier is not None:
            return await self._getTracks(f"http://{self.node.host}:{self.node.port}/loadtracks", {"identifier": identifier}, returnFirst)

    async def _getTracks(self, req: str, params: Optional[Dict[str, str]], returnFirst: bool) -> Optional[Union[Track, List[Track]]]:
        """Actual function which gets and processes the track info"""
        data, response = await self.node.getData(req, params)
        if response.status != 200:
            raise LavalinkException("Invalid response from lavalink")

        loadType = data.get("loadType")
        if loadType == "LOAD_FAILED":
            raise LoadTrackError(f"Track failed to load with data: {data}")
        elif loadType == "NO_MATCHES":
            return None
        elif loadType == "TRACK_LOADED":
            trackInfo = data["tracks"][0]
            return Track(trackInfo["track"], trackInfo["info"])
        elif loadType == "SEARCH_RESULT":
            trackInfo = data["tracks"]
            if returnFirst:
                return Track(trackInfo[0]["track"], trackInfo[0]["info"])
            else:
                return [Track(element["track"], element["info"]) for element in trackInfo]

    async def _getPlaylist(self, req: str, params: Optional[Dict[str, str]]) -> Optional[Playlist]:
        """Actual function which gets and processes the playlist info"""
        data, response = await self.node.getData(req, params)
        if response.status != 200:
            raise LavalinkException("Invalid response from lavalink")

        loadType = data.get("loadType")
        if loadType == "LOAD_FAILED":
            raise LoadTrackError(f"Playlist failed to load with data: {data}")
        elif loadType == "NO_MATCHES":
            return None
        elif loadType == "PLAYLIST_LOADED":
            playlistInfo = data["playlistInfo"]
            return Playlist(playlistInfo["name"], playlistInfo["selectedTrack"], data["tracks"])
