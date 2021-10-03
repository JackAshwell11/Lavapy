"""
Copyright (C) 2021 Aspect1103

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from typing import Dict, Union

from discord import VoiceRegion
from discord.ext.commands import Bot, AutoShardedBot

from .exceptions import NodeOccupied, InvalidIdentifier, NoNodesConnected
from .node import Node


class NodePool:
    _nodes: Dict[str, Node] = {}

    @classmethod
    def getNode(cls, identifier: str = None, region: VoiceRegion = None) -> Node:
        if not cls._nodes:
            raise NoNodesConnected("There are currently no nodes connected")

        if identifier is not None:
            try:
                node = cls._nodes[identifier]
                return node
            except KeyError:
                raise InvalidIdentifier(f"No nodes with the identifier <{identifier}>")
        elif region is not None:
            nodes = [node for node in cls._nodes.values() if node.region is region]
            if not nodes:
                raise NoNodesConnected(f"No nodes exist for region <{region}>")
        else:
            nodes = cls._nodes.values()
        return sorted(nodes, key=lambda x: x.playerCount)[0]

    @classmethod
    async def createNode(cls, bot: Union[Bot, AutoShardedBot], host: str, port: int, password: str, region: VoiceRegion, identifier: str) -> None:
        if identifier in cls._nodes:
            raise NodeOccupied(f"A node with the identifier <{identifier}> already exists")

        node = Node(bot, host, port, password, region, identifier)
        await node.connect()

        cls._nodes[identifier] = node
