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
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Tuple, Type, Union

from lavapy.tracks import MultiTrack, Playable, Track

if TYPE_CHECKING:
    from lavapy.pool import Node

__all__ = ("decodeSpotifyQuery",
           "SpotifyBase",
           "SpotifyTrack",
           "SpotifyPlaylist",
           "SpotifyAlbum")


def decodeSpotifyQuery(query: str) -> Type[Playable]:
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
    if re.compile("https://open\.spotify\.com/track").match(query):
        return SpotifyTrack
    elif re.compile("https://open\.spotify\.com/playlist").match(query):
        return SpotifyPlaylist
    elif re.compile("https://open\.spotify\.com/track/album").match(query):
        return SpotifyAlbum
    else:
        return SpotifyTrack


async def spotifyGetDetails(cls: Type[SpotifyBase], query: str, node: Node) -> Union[str, List[str]]:
    """|coro|

    Gets details about a Spotify track.

    Parameters
    ----------
    cls: Type[SpotifyPlayable]
        The Lavapy Spotify resource to get the search type for.
    query: str
        The query to search Spotify for.
    node: Node
        The Lavapy node to use for querying the Spotify web API.

    Returns
    -------
    Union[str, List[str]]
        A query string or list of query strings.
    """
    regexResult = re.compile("https://open\.spotify\.com/.+/(?P<identifier>.+)\?").match(query)
    if cls._spotifyType == "track":
        if not regexResult:
            return f"ytsearch:{query}"
        else:
            identifier = regexResult.group("identifier")
            async with node.spotifyClient.session.get(f"https://api.spotify.com/v1/tracks/{identifier}", headers=node.spotifyClient.authHeaders) as response:
                data = await response.json()
            return f'ytsearch:{data["artists"][0]["name"]} - {data["name"]}'
    elif cls._spotifyType == "playlist":
        url = f"https://api.spotify.com/v1/playlists/{regexResult.group('identifier')}/tracks"
    elif cls._spotifyType == "album":
        url = f"https://api.spotify.com/v1/albums/{regexResult.group('identifier')}/tracks"
    # noinspection PyUnboundLocalVariable
    async with node.spotifyClient.session.get(url, headers=node.spotifyClient.authHeaders) as response:
        data = await response.json()
    trackArr: List[Dict[str, Any]] = data["items"]
    nextUrl = data["next"]
    while nextUrl:
        async with node.spotifyClient.session.get(nextUrl, headers=node.spotifyClient.authHeaders) as response:
            data = await response.json()
        trackArr.extend(data["items"])
        nextUrl = data["next"]
    return [f'ytsearch:{track["track"]["artists"][0]["name"]} - {track["track"]["name"]}' for track in trackArr]


async def spotifyGetMultitrackName(cls: Type[SpotifyBase], query: str, node: Node) -> str:
    """|coro|

    Parameters
    ----------
    cls: Type[SpotifyPlayable]
        The Lavapy Spotify resource to create an instance of.
    query: str
        The query to search Spotify for.
    node: Node
        The Lavapy node to use for querying the Spotify web API.

    Returns
    -------
    str
        The multitrack's name.
    """
    regexResult = re.compile("https://open\.spotify\.com/.+/(?P<identifier>.+)\?").match(query)
    if cls._spotifyType == "track":
        return ""
    elif cls._spotifyType == "playlist":
        async with node.spotifyClient.session.get(f"https://api.spotify.com/v1/playlists/{regexResult.group('identifier')}", headers=node.spotifyClient.authHeaders) as response:
            data = await response.json()
    elif cls._spotifyType == "album":
        async with node.spotifyClient.session.get(f"https://api.spotify.com/v1/albums/{regexResult.group('identifier')}", headers=node.spotifyClient.authHeaders) as response:
            data = await response.json()
    return data["name"]


class SpotifyBase(Playable):
    """A class which abstracts away a couple functions used for all Spotify resources."""
    _spotifyType: str
    _queryGetter: Callable = spotifyGetDetails
    _getMultitrackName: Callable = spotifyGetMultitrackName


class SpotifyTrack(Track, SpotifyBase):
    """A track created using a search to Spotify."""
    _spotifyType: str = "track"

    def __repr__(self) -> str:
        return f"<Lavapy SpotifyTrack (YoutubeIdentifier={self.identifier})>"


class SpotifyPlaylist(MultiTrack, SpotifyBase):
    """A playlist created using a search to Spotify."""
    _spotifyType: str = "playlist"

    def __repr__(self) -> str:
        return f"<Lavapy SpotifyPlaylist (Name={self.name}) (Track count={len(self.tracks)})>"


class SpotifyAlbum(MultiTrack, SpotifyBase):
    """An album created using a search to Spotify."""
    _spotifyType: str = "album"
    _trackCls: Type[Track] = SpotifyTrack

    def __repr__(self) -> str:
        return f"<Lavapy SpotifyAlbum (Name={self.name}) (Track count={len(self.tracks)})>"
