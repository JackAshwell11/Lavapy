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
from typing import Dict, Union

from discord import VoiceRegion
from discord.ext.commands import Bot, AutoShardedBot

from .exceptions import NoNodesConnected, InvalidIdentifier, NodeOccupied
from .node import Node


_nodes: Dict[str, Node] = {}


def _getNode(identifier: str = None, region: VoiceRegion = None) -> Node:
    if not _nodes:
        raise NoNodesConnected("There are currently no nodes connected")
    if identifier is not None:
        try:
            node = _nodes[identifier]
            return node
        except KeyError:
            raise InvalidIdentifier(f"No nodes with the identifier <{identifier}>")
    elif region is not None:
        possibleNodes = [node for node in _nodes.values() if node.region is region]
        if not possibleNodes:
            raise NoNodesConnected(f"No nodes exist for region <{region}>")
    else:
        possibleNodes = _nodes.values()
    return sorted(possibleNodes, key=lambda x: len(x.players))[0]


async def createNode(bot: Union[Bot, AutoShardedBot], host: str, port: int, password: str, region: VoiceRegion, identifier: str) -> None:
    if identifier in _nodes:
        raise NodeOccupied(f"A node with the identifier <{identifier}> already exists")

    node = Node(bot, host, port, password, region, identifier)
    await node.connect()

    _nodes[identifier] = node
