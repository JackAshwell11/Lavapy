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
from .exceptions import NoNodesConnected, InvalidGuildID
from typing import Union
from discord.ext import commands
from discord import Guild
from discord.enums import VoiceRegion


class PylinkClient:
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]) -> None:
        self.bot = bot
        self.nodes = {}
        self.players = {}
        self.bot.add_listener(self.voiceUpdateHandler, "on_socket_response")

    def __repr__(self):
        return f"<Pylink Client>"

    def getBestNode(self, guild: Guild):
        return [node for node in sorted(self.nodes.values(), key=lambda x: x.players) if node.region == guild.region][0]

    async def createNode(self, host: str, port: int, password: str, region: VoiceRegion, identifier: str) -> None:
        self.nodes[identifier] = Node(self.bot, host, port, password, str(self.bot.user.id), region, identifier)

    async def createPlayer(self, guildID: int) -> Player:
        guild = self.bot.get_guild(guildID)
        if guild is None:
            raise InvalidGuildID(f"A guild with the ID <{guildID}> does not exist")
        if len(list(self.nodes.keys())) == 0:
            raise NoNodesConnected("There are currently no nodes connected")
        bestNode: Node = list(self.nodes.values())[0] if len(list(self.nodes.keys())) == 1 else self.getBestNode(guild)
        self.players[guildID] = Player(self.bot, bestNode, guild)
        self.nodes[bestNode.identifier].players += 1
        return self.players[guildID]

    async def voiceUpdateHandler(self, data):
        if data["t"] == "VOICE_SERVER_UPDATE":
            await self.players[int(data["d"]["guild_id"])].voiceServerUpdate(data["d"])
        elif data["t"] == "VOICE_STATE_UPDATE":
            if int(data["d"]["user_id"]) == self.bot.user.id:
                await self.players[int(data["d"]["guild_id"])].voiceStateUpdate(data["d"])
        elif data["d"] is not None:
            print(data)
