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
from typing import Union, List, Dict, Any, Optional

from discord import VoiceProtocol, VoiceChannel, Guild
from discord.ext.commands import Bot, AutoShardedBot

from .pool import _getNode
from .track import Track
from .equalizer import Equalizer


class Player(VoiceProtocol):
    def __init__(self, bot: Union[Bot, AutoShardedBot], channel: VoiceChannel) -> None:
        super().__init__(bot, channel)
        self.bot = bot
        self.channel = channel
        self.node = _getNode()
        self.volume: float = 100
        self._voiceState: Dict[str, Any] = {}
        self._track: Optional[Track] = None
        self._connected: bool = False
        self._paused: bool = False
        self._equalizer = Equalizer.flat()

    def __repr__(self) -> str:
        return f"<Pylink Player (ChannelID={self.channel.id}) (GuildID={self.channel.guild.id})>"

    def isConnected(self) -> bool:
        return self._connected

    def isPlaying(self) -> bool:
        return self.isConnected() and self._track is not None

    def isPaused(self) -> bool:
        return self._paused

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
        self._connected = True

    async def disconnect(self, *, force: bool = False) -> None:
        await self.channel.guild.change_voice_state(channel=None)
        self.node.playerCount -= 1

    async def getYoutubeTracks(self, query: str) -> List[Track]:
        return await self._getTracks(f"ytsearch:{query}")

    async def getSoundcloudTracks(self, query: str) -> List[Track]:
        return await self._getTracks(f"scsearch:{query}")

    async def _getTracks(self, query: str) -> List[Track]:
        songs = await self.node.getTracks(query)
        try:
            return [Track(element.get("track"), element.get("info")) for element in songs.get("tracks")]
        except TypeError:
            return []

    async def play(self, track: Track, replace: bool = True, startTime: int = 0, endTime: int = 0) -> None:
        if not replace:
            return
        newTrack = {
            "op": "play",
            "guildId": str(self.channel.guild.id),
            "track": track.id,
            "noReplace": not replace,
            "startTime": str(startTime)
        }
        if endTime > 0:
            newTrack["endTime"] = str(endTime)
        self._track = track
        await self.node.send(newTrack)

    async def stop(self) -> None:
        stop = {
            "op": "stop",
            "guildId": str(self.channel.guild.id)
        }
        self._track = None
        await self.node.send(stop)

    async def togglePause(self, pause: bool) -> None:
        pause = {
            "op": "pause",
            "guildId": str(self.channel.guild.id),
            "pause": pause
        }
        self._paused = pause
        await self.node.send(pause)

    async def pause(self) -> None:
        await self.togglePause(True)

    async def resume(self) -> None:
        await self.togglePause(False)

    async def seek(self, position: int) -> None:
        # TODO: Maybe add an if statement to check if position is above length of song
        seek = {
            "op": "seek",
            "guildId": str(self.channel.guild.id),
            "position": position
        }
        await self.node.send(seek)

    async def setVolume(self, volume: int) -> None:
        self.volume = max(min(volume, 1000), 0)
        volume = {
            "op": "volume",
            "guildId": str(self.channel.guild.id),
            "volume": self.volume
        }
        await self.node.send(volume)

    async def destroy(self) -> None:
        destroy = {
            "op": "destroy",
            "guildId": str(self.channel.guild.id)
        }
        await self.node.send(destroy)

    async def setEqualizer(self, eq: Equalizer) -> None:
        if not isinstance(eq, Equalizer):
            return
        self._equalizer = eq
        equalizer = {
            "op": "equalizer",
            "guildId": str(self.channel.guild.id),
            "bands": self._equalizer.eq
        }
        await self.node.send(equalizer)
