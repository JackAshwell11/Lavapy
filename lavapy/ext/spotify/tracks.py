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

from typing import TYPE_CHECKING

from lavapy.tracks import PartialResource

if TYPE_CHECKING:
    from lavapy.node import Node


class SpotifySearchable:
    _searchEndpoint: str = "https://api.spotify.com/v1/tracks/id"

    @classmethod
    async def search(cls, query: str, node: Node = None, returnFirst: bool = True, partial: bool = False):
        if partial:
            # noinspection PyTypeChecker
            return PartialResource(cls, query, True)
        if node is None:
            # Avoid a circular dependency with node.buildTrack()
            from lavapy.pool import NodePool
            node = NodePool.getNode()
        searchHeaders = {
            "Authorization": node.spotifyClient.accessToken,
            "Content-Type": "application/json"
        }
        f = await node.spotifyClient.session.get(f"cls._searchEndpoint/{query}", headers=node.spotifyClient)
        print(f)


class SpotifyIdentifiable:
    _searchEndpoint: str = "https://api.spotify.com/v1/search?type="

    @classmethod
    async def get(cls, identifier: str, node: Node = None, partial: bool = False):
        pass


class Track:
    pass


class MultiTrack:
    pass
