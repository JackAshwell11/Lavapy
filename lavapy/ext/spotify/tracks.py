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
from typing import TYPE_CHECKING, Optional, Callable, Union, Tuple, List, Dict, Type, Any

from lavapy.tracks import Playable, Track, MultiTrack, YoutubeTrack
from .exceptions import InvalidSpotifyClient

if TYPE_CHECKING:
    from lavapy.node import Node

__all__ = ("SpotifyPlayable",
           "SpotifyTrack",
           "SpotifyPlaylist")


# async def spotifyQueryProcessor(cls: Union[SpotifyTrack, SpotifyPlaylist], query: str, node: Node) -> Tuple[Union[str, List[str]], Optional[str]]:
#     """|coro|
#
#     Parameters
#     ----------
#     cls: Union[SpotifyTrack, SpotifyPlaylist]
#         The Spotify resource to query the web API for details about.
#     query: str
#         The query to send to Spotify's web API.
#     node: Node
#         The Lavapy node to use for querying the Spotify web API.
#
#     Raises
#     ------
#     InvalidSpotifyClient
#         The provided Lavapy node's Spotify client is invalid
#
#     Returns
#     -------
#     Tuple[Union[str, List[str]], Optional[str]]
#         A query or list of queries which can be used to search Lavalink for. There is also a multitrack name for use with :meth:`spotifyExtensionIterator()`.
#     """
#     if node.spotifyClient is None:
#         raise InvalidSpotifyClient(f"{node.identifier}'s SpotifyClient is invalid.")
#     regexResult = re.compile("https://open\.spotify\.com/.+/(?P<identifier>.+)\?").match(query)
#     if cls._spotifyType == "track":
#         if not regexResult:
#             async with node.spotifyClient.session.get("https://api.spotify.com/v1/search?type=track", headers=node.spotifyClient.authHeaders, params={"q": query}) as response:
#                 data = await response.json()
#             data = data["tracks"]["items"][0]
#         else:
#             identifier = regexResult.group("identifier")
#             async with node.spotifyClient.session.get(f"https://api.spotify.com/v1/tracks/{identifier}", headers=node.spotifyClient.authHeaders) as response:
#                 data = await response.json()
#         return f'ytsearch:{data["artists"][0]["name"]} - {data["name"]}', None
#     elif cls._spotifyType == "playlist":
#         identifier = regexResult.group("identifier")
#         async with node.spotifyClient.session.get(f"https://api.spotify.com/v1/playlists/{identifier}", headers=node.spotifyClient.authHeaders) as response:
#             data = await response.json()
#         trackArr: List[Dict[str, Any]] = data["tracks"]["items"]
#         nextUrl = data["tracks"]["next"]
#         playlistName = data["name"]
#         while nextUrl:
#             async with node.spotifyClient.session.get(data["tracks"]["next"], headers=node.spotifyClient.authHeaders) as response:
#                 data = await response.json()
#             trackArr.extend(data["items"])
#             nextUrl = data["next"]
#         return [f'ytsearch:{track["track"]["artists"][0]["name"]} - {track["track"]["name"]}' for track in trackArr], playlistName
#     elif cls._spotifyType == "album":
#         pass
#
#
# async def spotifyExtensionIterator(cls: Union[Type[SpotifyPlaylist]], query: List[str], node: Node, multitrackName: str) -> Union[SpotifyPlaylist]:
#     """|coro|
#
#     Parameters
#     ----------
#     cls: Union[Type[SpotifyPlaylist]]
#         The Spotify resource to create an instance of.
#     query: List[str]
#         A list of strings to query Lavalink for.
#     node: Node
#         The Lavapy node to use for querying Lavalink.
#     multitrackName
#
#     Returns
#     -------
#     Union[SpotifyPlaylist]
#         A Lavapy Spotify playlist which can be used for playing music.
#     """
#     trackArr = []
#     for count, trackQuery in enumerate(query):
#         tracks = await node.getTracks(YoutubeTrack, trackQuery)
#         trackArr.append(tracks[0])
#         if count == 1:
#             break
#     return cls(multitrackName, trackArr)
#
#
# async def spotifyReturnProcessor(tracks: List[SpotifyTrack], search: bool, returnFirst: bool) -> Optional[Union[SpotifyTrack, List[SpotifyTrack]]]:
#     """|coro|
#
#     Parameters
#     ----------
#     tracks: List[SpotifyTrack]
#         A list of Spotify tracks to process.
#     search: bool
#         Whether the search was a query or identifier search.
#     returnFirst: bool
#         Whether to return only the first result or not.
#
#     Returns
#     -------
#     Optional[Union[SpotifyTrack, List[SpotifyTrack]]]
#         A Lavapy Spotify track or list of tracks which can be used for playing music
#     """
#     if search and not returnFirst:
#         return tracks
#     return tracks[0]


class SpotifyPlayable:
    """The base class for all Lavapy Spotify resources. This supports both query searches and identifier searches."""
    _spotifyType: str

    @classmethod
    async def search(cls, query: str, node: Node = None, search: bool = True, returnFirst: bool = True, partial: bool = False) -> Optional[Union[Track, List[Track], PartialResource, MultiTrack]]:
        pass


class SpotifyTrack(Track, SpotifyPlayable):
    """A track created using a search to Spotify."""
    _spotifyType: str = "track"

    def __repr__(self) -> str:
        return f"<Lavapy SpotifyTrack (YoutubeIdentifier={self.identifier})>"


class SpotifyPlaylist(MultiTrack, SpotifyPlayable):
    """A playlist created using a search to Spotify."""
    _spotifyType: str = "playlist"

    def __repr__(self) -> str:
        return f"<Lavapy SpotifyPlaylist>"
