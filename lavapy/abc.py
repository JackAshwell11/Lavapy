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
from typing import Optional, Dict, Union, List, TYPE_CHECKING

from .exceptions import LavalinkException, LoadTrackError

if TYPE_CHECKING:
    from .node import Node
    from .tracks import YoutubePlaylist, Track

__all__ = ("Playable",)

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
