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

import re
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type, Union

import lavapy

if TYPE_CHECKING:
    from .pool import Node

__all__ = ("decodeQuery",
           "Playable",
           "PartialResource",
           "Track",
           "MultiTrack",
           "YoutubeTrack",
           "YoutubeMusicTrack",
           "SoundcloudTrack",
           "LocalTrack",
           "YoutubePlaylist")


def decodeQuery(query: str) -> Type[Playable]:
    """
    Decodes a query into a :class:`Playable` type which can be searched.

    Parameters
    ----------
    query: str
        The query to decode.

    Returns
    -------
    Type[Playable]
        The playable type which can be searched.
    """
    if re.compile("https://www.youtube.com/watch\?v=.+").match(query):
        return YoutubeTrack
    elif re.compile("https://music.youtube.com/watch\?v=.+").match(query):
        return YoutubeMusicTrack
    elif re.compile("https://soundcloud.com/(?!discover).+").match(query) and "sets" not in query:
        return SoundcloudTrack
    elif re.compile("https://cdn.discordapp.com/.+.mp3").match(query):
        return LocalTrack
    elif re.compile("https://www.youtube.com/playlist\?list=.+").match(query):
        return YoutubePlaylist
    else:
        return YoutubeTrack


async def defaultQueryGetter(cls: Type[Playable], query: str, _) -> str:
    """|coro|

    Forms the query for a specific :class:`Playable`.

    Parameters
    ----------
    cls: Type[Playable]
        The self to get the search type for.
    query: str
        The query to modify with a search type.

    Returns
    -------
    str
        The modified query.
    """
    if not re.compile("https://.+/").match(query):
        return f"{cls._searchType}:{query}"
    return query


class Playable:
    """
    The base class for all Lavapy resources. This supports both query searches and identifier searches.

    .. warning::
        This class should not be created manually. Instead use a subclass of :class:`Track` or :class:`MultiTrack`.
    """
    _searchType: str
    _trackCls: Optional[Type[Track]]
    _queryGetter: Callable = defaultQueryGetter
    _getMultitrackName: Optional[Callable] = None

    @classmethod
    async def search(cls, query: str, node: Node = None, returnFirst: bool = True, partial: bool = False) -> Optional[Union[Playable, Track, List[Track], PartialResource, List[PartialResource], MultiTrack]]:
        """|coro|

        Performs a search to Lavalink for a specific resource.

        Parameters
        ----------
        query: str
            The query to search for.
        node: Node
            The Lavapy Node to use for searching. If this is not supplied, a random one from the node pool will be retrieved.
        returnFirst: bool
            Whether to return only the first result or not.
        partial: bool
            Whether to return a Lavapy partial resource or not.

        Returns
        -------
        Optional[Union[Playable, Track, List[Track], PartialResource, List[PartialResource], MultiTrack]]
            A Lavapy resource or a list of resources which can be used to play music.
        """
        if node is None:
            node = lavapy.NodePool.extension(cls)
        newQuery = await cls._queryGetter(cls, query, node)
        if partial:
            if isinstance(newQuery, list):
                # This will only run with extensions
                multitrackName = await cls._getMultitrackName(cls, query, node)
                return cls(multitrackName, [PartialResource(YoutubeTrack, temp) for temp in newQuery])
            return PartialResource(cls, newQuery)
        if isinstance(newQuery, str):
            tracks = await node.getTracks(cls, newQuery)
        else:
            temp = []
            for i in newQuery:
                result = await node.getTracks(YoutubeTrack, i)
                temp.append(result[0])
            multitrackName = await cls._getMultitrackName(cls, query, node)
            tracks = cls(multitrackName, temp)
        if tracks is not None:
            if isinstance(tracks, list) and returnFirst:
                return tracks[0]
            return tracks

    def __init__(self, *data: Any) -> None:
        """This is just here to stop :meth:`Node.getTracks()` being upset about unexpected arguments."""


class PartialResource:
    """
    A class which searches for the given query at playtime.

    .. warning::
        It is advised not to create this manually, however, it is possible to do so.

    Parameters
    ----------
    cls: Type[Playable]
        The resource to create a instance of at playtime.
    query: str
        The query to search for at playtime.

    .. warning::
        This object will only search for the given query at playtime. Full resource information will be missing until it has been searched. It is advised not to create this manually, however, it is possible to do so.
    """
    def __init__(self, cls: Type[Playable], query: str) -> None:
        self._cls = cls
        self._query: str = query

    def __repr__(self) -> str:
        return f"<Lavapy PartialResource (Cls={self.cls}) (Query={self.query})>"

    @property
    def cls(self) -> Type[Playable]:
        """Returns the resource which will be created at playtime."""
        return self._cls

    @property
    def query(self) -> str:
        """Returns the query which will be searched for at playtime."""
        return self._query


class Track:
    """
    The base class for all Lavapy Track objects.

    .. warning::
        It is advised not to create this manually, however, it is possible to do so.

    Parameters
    ----------
    id: str
        The unique base64 track ID which can be used to rebuild a track.
    info: Dict[str, Any]
        The raw track info.
    """
    def __init__(self, id: str, info: Dict[str, Any]) -> None:
        self._id: str = id
        self._info: Dict[str, Any] = info
        self._identifier: str = info["identifier"]
        self._isSeekable: bool = info["isSeekable"]
        self._author: str = info["author"]
        self._length: int = info["length"]
        self._isStream: bool = info["isStream"]
        self._type: str = info["sourceName"]
        self._title: str = info["title"]
        self._uri: str = info["uri"]

    def __repr__(self) -> str:
        return f"<Lavapy Track (Identifier={self.identifier}) (Type={self.type})>"

    @property
    def id(self) -> str:
        """Returns the base64 track ID."""
        return self._id

    @property
    def identifier(self) -> str:
        """Returns the track's unique identifier."""
        return self._identifier

    @property
    def isSeekable(self) -> bool:
        """Returns whether a track is seekable or not."""
        return self._isSeekable

    @property
    def author(self) -> str:
        """Returns the author of the track."""
        return self._author

    @property
    def length(self) -> int:
        """Returns the duration of the track in seconds."""
        return self._length

    @property
    def isStream(self) -> bool:
        """Returns whether the track is a stream or not."""
        return self._isStream

    @property
    def type(self) -> str:
        """Returns the source site of the track."""
        return self._type

    @property
    def title(self) -> str:
        """Returns the title of the track."""
        return self._title

    @property
    def uri(self) -> str:
        """Returns the URI of the track."""
        return self._uri


class MultiTrack:
    """
    The base class for all Lavapy MultiTrack resources. These could be playlists or albums.

    .. warning::
        It is advised not to create this manually, however, it is possible to do so.

    Parameters
    ----------
    name: str
        The name of the playlist.
    tracks: List[Track]
        The playlist's tracks as a list of Lavapy Track objects.
    """
    def __init__(self, name: str, tracks: List[Track]) -> None:
        self._name: str = name
        self._tracks: List[Track] = tracks

    def __repr__(self) -> str:
        return f"<Lavapy MultiTrack (Name={self.name}) (Track count={len(self.tracks)})>"

    @property
    def name(self) -> str:
        """Returns the name of the playlist."""
        return self._name

    @property
    def tracks(self) -> List[Track]:
        """Returns the playlist's tracks."""
        return self._tracks


class YoutubeTrack(Track, Playable):
    """A track created using a search to Youtube."""
    _searchType: str = "ytsearch"

    def __repr__(self) -> str:
        return f"<Lavapy YoutubeTrack (Identifier={self.identifier})>"

    @property
    def thumbnail(self) -> str:
        """Returns the URI to the thumbnail of this track."""
        return f"https://img.youtube.com/vi/{self.identifier}/maxresdefault.jpg"


class YoutubeMusicTrack(Track, Playable):
    """A track created using a search to Youtube Music."""
    _searchType: str = "ytmsearch"

    def __repr__(self) -> str:
        return f"<Lavapy YoutubeMusicTrack (Identifier={self.identifier})>"


class SoundcloudTrack(Track, Playable):
    """A track created using a search to Soundcloud."""
    _searchType: str = "scsearch"

    def __repr__(self) -> str:
        return f"<Lavapy SoundcloudTrack (Identifier={self.identifier})>"


class LocalTrack(Track, Playable):
    """A track created using a search to a Discord mp3 file."""

    def __repr__(self) -> str:
        return f"<Lavapy LocalTrack (Identifier={self.identifier})>"


class YoutubePlaylist(MultiTrack, Playable):
    """A playlist created using a search to Youtube."""
    _trackCls: Type[Track] = YoutubeTrack

    def __repr__(self) -> str:
        return f"<Lavapy YoutubePlaylist (Name={self.name}) (Track count={len(self.tracks)})>"
