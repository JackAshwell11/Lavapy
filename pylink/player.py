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
from .exceptions import InvalidGuildID, InvalidChannelID
from .node import Node
from typing import Union, Dict
from discord.ext import commands
from discord import Guild, VoiceChannel


class Player:
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot], node: Node, guildID: int) -> None:
        self._bot = bot
        self._node = node
        if self._bot.get_guild(guildID) is None:
            raise InvalidGuildID("temp")
        self._guildID = guildID
        self._voiceState = {}

    def __repr__(self):
        return f"<Pylink Player (GuildID={self._guildID})>"

    async def voiceStateUpdate(self, data):
        self._voiceState.update({"sessionId": data["session_id"]})
        await self.sendVoiceUpdate()

    async def voiceServerUpdate(self, data):
        self._voiceState.update({"event": data})
        await self.sendVoiceUpdate()

    async def sendVoiceUpdate(self):
        if {"sessionId", "event"} == self._voiceState.keys():
            voiceUpdate = {
                "op": "voiceUpdate",
                "guildId": str(self._guildID),
                "sessionId": self._voiceState["sessionId"],
                "event": self._voiceState["event"]
            }
            await self._node.send(voiceUpdate)

    async def connect(self, channelID: int) -> None:
        guild: Guild = self._bot.get_guild(self._guildID)
        channel: VoiceChannel = guild.get_channel(channelID)
        if channel is None:
            raise InvalidChannelID("temp")
        await guild.change_voice_state(channel=channel)

    async def getYoutubeTracks(self, query: str):
        songs = await self._node.getTracks(f"ytsearch:{query}")
        return songs["tracks"]

    async def play(self, track: Dict[str, Union[str, Dict[str, Union[str, bool, int]]]]):
        newTrack = {
            "op": "play",
            "guildId": str(self._guildID),
            "track": track["track"]
        }
        await self._node.send(newTrack)
