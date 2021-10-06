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
from typing import Union

from discord import VoiceProtocol, VoiceChannel
from discord.ext.commands import Bot, AutoShardedBot

from .pool import _getNode


class Player(VoiceProtocol):
    def __init__(self, bot: Union[Bot, AutoShardedBot], channel: VoiceChannel) -> None:
        super().__init__(bot, channel)
        self.bot = bot
        self.channel = channel
        self.node = _getNode()
        self._voiceState = {}

    def __repr__(self) -> str:
        return f"<Pylink Player (ChannelID={self.channel.id}) (GuildID={self.channel.guild.id})>"

    async def on_voice_state_update(self, data: dict) -> None:
        self._voiceState.update({"sessionId": data["session_id"]})
        await self.sendVoiceUpdate()

    async def on_voice_server_update(self, data: dict) -> None:
        self._voiceState.update({"event": data})
        await self.sendVoiceUpdate()

    async def sendVoiceUpdate(self) -> None:
        if {"sessionId", "event"} == self._voiceState.keys():
            voiceUpdate = {
                "op": "voiceUpdate",
                "guildId": str(self.channel.guild.id),
                "sessionId": self._voiceState["sessionId"],
                "event": self._voiceState["event"]
            }
            await self.node.send(voiceUpdate)

    async def connect(self, timeout: float, reconnect: bool) -> None:
        await self.channel.guild.change_voice_state(channel=self.channel)
        self.node.playerCount += 1

    async def disconnect(self, *, force: bool = False) -> None:
        await self.channel.guild.change_voice_state(channel=None)
        self.node.playerCount -= 1

    async def getYoutubeTracks(self, query: str) -> dict:
        songs = await self.node.getTracks(f"ytsearch:{query}")
        return songs["tracks"]

    async def play(self, track: dict) -> None:
        newTrack = {
            "op": "play",
            "guildId": str(self.channel.guild.id),
            "track": track["track"]
        }
        await self.node.send(newTrack)
