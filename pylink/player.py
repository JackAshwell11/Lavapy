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
from .exceptions import InvalidChannelID
from .node import Node
from typing import Union, Dict
from discord.ext import commands
from discord import Guild, VoiceChannel


class Player:
    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot], node: Node, guild: Guild) -> None:
        self.bot = bot
        self.node = node
        self.guild = guild
        self._voiceState = {}

    def __repr__(self):
        return f"<Pylink Player (GuildID={self.guild.id})>"

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
                "guildId": str(self.guild.id),
                "sessionId": self._voiceState["sessionId"],
                "event": self._voiceState["event"]
            }
            await self.node.send(voiceUpdate)

    async def connect(self, channelID: int) -> None:
        channel: VoiceChannel = self.guild.get_channel(channelID)
        if channel is None:
            raise InvalidChannelID("temp")
        await self.guild.change_voice_state(channel=channel)

    async def getYoutubeTracks(self, query: str):
        songs = await self.node.getTracks(f"ytsearch:{query}")
        return songs["tracks"]

    async def play(self, track: Dict[str, Union[str, Dict[str, Union[str, bool, int]]]]):
        newTrack = {
            "op": "play",
            "guildId": str(self.guild.id),
            "track": track["track"]
        }
        await self.node.send(newTrack)
