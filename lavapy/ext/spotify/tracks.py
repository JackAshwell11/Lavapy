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

from typing import TYPE_CHECKING, Optional, Union, List

from lavapy.tracks import PartialResource, YoutubeTrack

if TYPE_CHECKING:
    from lavapy.node import Node

__all__ = ("SpotifySearchable",
           "SpotifyIdentifiable",
           "SpotifyTrack")


class SpotifySearchable:
    _searchEndpoint: str = "https://api.spotify.com/v1/search?type="
    _searchType: str = ""

    @classmethod
    async def search(cls, query: str, node: Node = None, returnFirst: bool = True, partial: bool = False) -> Optional[Union[SpotifyTrack, PartialResource, List[SpotifyTrack]]]:
        if partial:
            # noinspection PyTypeChecker
            return PartialResource(cls, query, True)
        if node is None:
            # Avoid a circular dependency with node.buildTrack()
            from lavapy.pool import NodePool
            node = NodePool.getNode()
        searchParams = {
            "q": query
        }
        async with node.spotifyClient.session.get(f"{cls._searchEndpoint}{cls._searchType}", headers=node.spotifyClient.authHeaders, params=searchParams) as response:
            data = await response.json()
        data = data["tracks"]["items"][0]
        artistName = data["artists"][0]["name"]
        trackName = data["name"]
        tracks = await node.getTracks(YoutubeTrack, f"{artistName} - {trackName}")
        if tracks is not None:
            if returnFirst:
                return SpotifyTrack(tracks[0])
            return [SpotifyTrack(track) for track in tracks]


class SpotifyIdentifiable:
    _searchEndpoint: str = "https://api.spotify.com/v1/tracks/id"

    @classmethod
    async def get(cls, identifier: str, node: Node = None, partial: bool = False):
        pass


class SpotifyTrack(SpotifySearchable, SpotifyIdentifiable):
    _searchType: str = "track"

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"<Lavapy SpotifyTrack>"
