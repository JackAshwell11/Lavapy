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
import aiohttp
from urllib.parse import quote
from typing import Union, Dict

from discord.enums import VoiceRegion
from discord.ext.commands import Bot, AutoShardedBot

from .websocket import Websocket
from .exceptions import NoNodesConnected, InvalidIdentifier, NodeOccupied


class Node:
    def __init__(self, bot: Union[Bot, AutoShardedBot], host: str, port: int, password: str, region: VoiceRegion, identifier: str) -> None:
        self.bot = bot
        self.host = host
        self.port = port
        self.password = password
        self.region = region
        self.identifier = identifier
        self.session = aiohttp.ClientSession()
        self.playerCount = 0
        self._websocket = None

    def __repr__(self) -> str:
        return f"<Pylink Node (Domain={self.host}:{self.port}) (Identifier={self.identifier}) (Region={self.region})>"

    async def connect(self):
        self._websocket = Websocket(self)

    async def getTracks(self, query: str) -> dict:
        destination = f"http://{self.host}:{self.port}/loadtracks?identifier={quote(query)}"
        headers = {
            "Authorization": self.password
        }
        async with await self._websocket.get(destination, headers) as req:
            if req.status == 200:
                return await req.json()

    async def send(self, payload: dict) -> None:
        await self._websocket.send(payload)


def getNode(identifier: str = None, region: VoiceRegion = None) -> Node:
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
    return sorted(possibleNodes, key=lambda x: x.playerCount)[0]


async def createNode(bot: Union[Bot, AutoShardedBot], host: str, port: int, password: str, region: VoiceRegion, identifier: str) -> None:
    if identifier in _nodes:
        raise NodeOccupied(f"A node with the identifier <{identifier}> already exists")

    node = Node(bot, host, port, password, region, identifier)
    await node.connect()

    _nodes[identifier] = node


_nodes: Dict[str, Node] = {}
