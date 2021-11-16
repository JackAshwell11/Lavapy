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
from typing import TYPE_CHECKING, Optional, Union, Tuple, List, Dict, Type, Any

from lavapy.tracks import PartialResource, Track, MultiTrack, YoutubeTrack
from .exceptions import InvalidSpotifyClient

if TYPE_CHECKING:
    from lavapy.node import Node

__all__ = ("SpotifyPlayable",
           "SpotifyTrack",
           "SpotifyPlaylist",
           "SpotifyAlbum")


async def getDetails(cls: Type[SpotifyPlayable], query: str, node: Node) -> Tuple[Union[str, List[str]], Optional[str]]:
    """|coro|

    Gets details about a Spotify track.

    Parameters
    ----------
    cls: Type[SpotifyPlayable]
        The Lavapy Spotify resource to create an instance of.
    query: str
        The query to search Spotify for.
    node: Node
        The Lavapy node to use for querying the Spotify web API.

    Raises
    ------
    InvalidSpotifyClient
        The provided Lavapy node's Spotify client is invalid

    Returns
    -------
    Tuple[Union[str, List[str]], Optional[str]]
        A tuple containing a Youtube query or a list of Youtube query as well as the multitrack name.
    """
    if node.spotifyClient is None:
        raise InvalidSpotifyClient(f"{node.identifier}'s SpotifyClient is invalid.")
    regexResult = re.compile("https://open\.spotify\.com/.+/(?P<identifier>.+)\?").match(query)
    if cls._spotifyType == "track":
        if not regexResult:
            return f"ytsearch:{query}", None
        else:
            identifier = regexResult.group("identifier")
            async with node.spotifyClient.session.get(f"https://api.spotify.com/v1/tracks/{identifier}", headers=node.spotifyClient.authHeaders) as response:
                data = await response.json()
            return f'ytsearch:{data["artists"][0]["name"]} - {data["name"]}', None
    elif cls._spotifyType == "playlist":
        async with node.spotifyClient.session.get(f"https://api.spotify.com/v1/playlists/{regexResult.group('identifier')}", headers=node.spotifyClient.authHeaders) as response:
            data = await response.json()
        trackArr: List[Dict[str, Any]] = data["tracks"]["items"]
        nextUrl = data["tracks"]["next"]
        playlistName = data["name"]
        while nextUrl:
            async with node.spotifyClient.session.get(nextUrl, headers=node.spotifyClient.authHeaders) as response:
                data = await response.json()
            trackArr.extend(data["items"])
            nextUrl = data["next"]
        return [f'ytsearch:{track["track"]["artists"][0]["name"]} - {track["track"]["name"]}' for track in trackArr], playlistName
    elif cls._spotifyType == "album":
        async with node.spotifyClient.session.get(f"https://api.spotify.com/v1/albums/{regexResult.group('identifier')}", headers=node.spotifyClient.authHeaders) as response:
            data = await response.json()
        trackArr: List[Dict[str, Any]] = data["tracks"]["items"]
        nextUrl = data["tracks"]["next"]
        playlistName = data["name"]
        while nextUrl:
            async with node.spotifyClient.session.get(nextUrl, headers=node.spotifyClient.authHeaders) as response:
                data = await response.json()
            trackArr.extend(data["items"])
            nextUrl = data["next"]
        return [f'ytsearch:{track["artists"][0]["name"]} - {track["name"]}' for track in trackArr], playlistName


class SpotifyPlayable:
    """
    The base class for all Lavapy Spotify resources. This supports both query searches and identifier searches.

    .. warning::
        This class should not be created manually. Instead use :class:`SpotifyTrack`, :class:`SpotifyPlaylist` or :class:`SpotifyAlbum`.
    """
    _spotifyType: str

    @classmethod
    async def search(cls, query: str, node: Node = None, returnFirst: bool = True, partial: bool = False) -> Optional[Union[Track, List[Track], PartialResource, MultiTrack]]:
        """|coro|

        Performs a search to Lavalink for a specific Spotify resource.

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
        Optional[Union[Track, List[Track], PartialResource, MultiTrack]]
            A Lavapy resource or a list of resources which can be used to play music.
        """
        if node is None:
            # Avoid a circular dependency with node.buildTrack()
            from lavapy.pool import NodePool
            node = NodePool.getNode()
        query, multitrackName = await getDetails(cls, query, node)
        if partial:
            if isinstance(query, list):
                # noinspection PyTypeChecker
                return cls(multitrackName, [PartialResource(SpotifyTrack, temp) for temp in query])
            return PartialResource(cls, query)
        if isinstance(query, str):
            tracks = await node.getTracks(cls, query)
        else:
            temp = []
            for qry in query:
                result = await node.getTracks(cls, qry)
                temp.append(result[0])
            tracks = cls(multitrackName, temp)
        if tracks is not None:
            if isinstance(tracks, list) and returnFirst:
                return tracks[0]
            return tracks

    def __init__(self, *data: Any) -> None:
        """This is just here to stop :meth:`Node.getTracks()` being upset about unexpected arguments."""


class SpotifyTrack(Track, SpotifyPlayable):
    """A track created using a search to Spotify."""
    _spotifyType: str = "track"

    def __repr__(self) -> str:
        return f"<Lavapy SpotifyTrack (YoutubeIdentifier={self.identifier})>"


class SpotifyPlaylist(MultiTrack, SpotifyPlayable):
    """A playlist created using a search to Spotify."""
    _spotifyType: str = "playlist"

    def __repr__(self) -> str:
        return f"<Lavapy SpotifyPlaylist (Track count={len(self.tracks)})>"


class SpotifyAlbum(MultiTrack, SpotifyPlayable):
    """An album created using a search to Spotify."""
    _spotifyType: str = "album"

    def __repr__(self) -> str:
        return f"<Lavapy SpotifyAlbum (Track count={len(self.tracks)})>"
