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
import random
from typing import Dict, Union, Optional

from discord import VoiceRegion
from discord.ext.commands import Bot, AutoShardedBot

from .exceptions import NoNodesConnected, InvalidIdentifier, NodeOccupied
from .node import Node

__all__ = ("NodePool",)


class NodePool:
    """
    Lavapy NodePool class. This holds all the :class:'Node' objects created with :meth:`create_node()`.
    """
    _nodes: Dict[str, Node] = {}

    @property
    def nodes(self) -> Dict[str, Node]:
        """A mapping of identifiers to :class:'Node' objects."""
        return self._nodes


    @classmethod
    def getNode(cls, identifier: Optional[str] = None, region: Optional[VoiceRegion] = None) -> Node:
        """
        Retrieves a :class:`Node` either based on identifier, voice region or neither (randomly).

        Parameters
        ----------
        identifier: Optional[str]
            The unique identifier for the desired node.
        region: Optional[:class:`VoiceRegion`]
            The VoiceRegion a specific node is assigned to.

        Raises
        ------
        InvalidIdentifier
            No nodes exists with the given identifier.
        NoNodesConnected
            There are currently no nodes connected with the provided options.

        Returns
        -------
        Node
            A Lavapy :class:`Node` object.
        """
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected")
        if identifier is not None:
            try:
                node = cls._nodes[identifier]
                return node
            except KeyError:
                raise InvalidIdentifier(f"No nodes with the identifier <{identifier}>")
        elif region is not None:
            possibleNodes = [node for node in cls._nodes.values() if node.region is region]
            if not possibleNodes:
                raise NoNodesConnected(f"No nodes exist for region <{region}>")
        else:
            possibleNodes = cls._nodes.values()
        return sorted(possibleNodes, key=lambda x: len(x.players))[0]


    @classmethod
    async def createNode(cls, bot: Union[Bot, AutoShardedBot], host: str, port: int, password: str, region: Optional[VoiceRegion] = None, identifier: Optional[str] = None) -> None:
        """
        Creates a Lavapy :class:`Node` object and stores it for later use.

        Parameters
        ----------
        bot: Union[:class:`Bot`, :class:`AutoShardedBot`]
            The discord.py :class:`Bot` or :class:`AutoShardedBot` object.
        host: str
            The IP address of the Lavalink server.
        port: int
            The port of the Lavalink server.
        password: str
            The password to the Lavalink server.
        region: Optional[:class:`VoiceRegion`]
            The discord.py :class:`VoiceRegion` to assign to this node.
        identifier: Optional[str]
            The unique identifier for this node. If not supplied, it will be generated for you.

        Raises
        ------
        NodeOccupied
            If a node with the identifier already exists.
        """
        if identifier is None:
            identifier = "".join(random.choices(string.ascii_letters + string.digits, k=8))

        if identifier in cls._nodes:
            raise NodeOccupied(f"A node with the identifier <{identifier}> already exists")

        node = Node(bot, host, port, password, region, identifier)
        await node.connect()

        cls._nodes[identifier] = node
