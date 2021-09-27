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
from .node import Node
from .player import Player
from .exceptions import NoNodesConnected
from typing import Union
from discord.ext import commands


class PylinkClient:
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        self.bot = bot
        self._node = None
        self._player = None

    def __repr__(self):
        return f"<Pylink Client>"

    async def createNode(self, host: str, port: int, password: str, identifier: str) -> None:
        self._node = Node(host, port, password, str(self.bot.user.id), identifier)

    async def createPlayer(self, guildID: int) -> Player:
        if self._node is None:
            raise NoNodesConnected("There are currently no nodes connected")
        self._player = Player(self.bot, self._node, guildID)
        return self._player

    async def voiceUpdateHandler(self, data):
        if data["t"] == "VOICE_STATE_UPDATE":
            await self._player.voiceStateUpdate(data["d"])
        elif data["t"] == "VOICE_SERVER_UPDATE":
            await self._player.voiceServerUpdate(data["d"])
