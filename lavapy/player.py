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
import logging
from typing import Union, List, Optional, Any, Dict

from discord import VoiceProtocol, VoiceChannel, Guild
from discord.ext.commands import Bot, AutoShardedBot

from .equalizer import Equalizer
from .exceptions import InvalidIdentifier
from .pool import _getNode
from .tracks import Track
from .node import Node

__all__ = ("Player",)

logger = logging.getLogger(__name__)


class Player(VoiceProtocol):
    def __init__(self, bot: Union[Bot, AutoShardedBot], channel: VoiceChannel) -> None:
        super().__init__(bot, channel)
        self.bot: Union[Bot, AutoShardedBot] = bot
        self.channel: VoiceChannel = channel
        self.node: Optional[Node] = _getNode()
        self._voiceState: Dict[str, Any] = {}
        self._track: Optional[Track] = None
        self._connected: bool = False
        self._paused: bool = False
        self._volume: int = 100
        self._equalizer: Equalizer = Equalizer.flat()

    def __repr__(self) -> str:
        return f"<Lavapy Player (ChannelID={self.channel.id}) (GuildID={self.guild.id})>"

    @property
    def guild(self) -> Guild:
        return self.channel.guild

    @property
    def track(self) -> Track:
        return self._track

    @property
    def position(self) -> float:
        if not self.isPlaying():
            return 0

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
                "guildId": str(self.guild.id),
                "sessionId": self._voiceState["sessionId"],
                "event": self._voiceState["event"]
            }
            await self.node.send(voiceUpdate)

    async def connect(self, timeout: float, reconnect: bool) -> None:
        await self.guild.change_voice_state(channel=self.channel)
        self.node.playerCount += 1
        self._connected = True

    async def disconnect(self, *, force: bool = False) -> None:
        await self.guild.change_voice_state(channel=None)
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

    async def play(self, track: Track, startTime: int = 0, endTime: int = 0, volume: int = 100, replace: bool = True, pause: bool = False) -> None:
        if not replace:
            return
        newTrack = {
            "op": "play",
            "guildId": str(self.guild.id),
            "track": track.id,
            "startTime": str(startTime),
            "volume": str(volume),
            "noReplace": not replace,
            "pause": pause
        }
        if endTime > 0:
            newTrack["endTime"] = str(endTime)
        self._track = track
        self._volume = volume
        await self.node.send(newTrack)

    async def stop(self) -> None:
        stop = {
            "op": "stop",
            "guildId": str(self.guild.id)
        }
        self._track = None
        await self.node.send(stop)

    async def togglePause(self, pause: bool) -> None:
        pause = {
            "op": "pause",
            "guildId": str(self.guild.id),
            "pause": pause
        }
        self._paused = pause
        await self.node.send(pause)

    async def pause(self) -> None:
        await self.togglePause(True)

    async def resume(self) -> None:
        await self.togglePause(False)

    async def seek(self, position: int) -> None:
        if position > self._track.length:
            raise InvalidIdentifier("Seek position is bigger than track length")
        seek = {
            "op": "seek",
            "guildId": str(self.guild.id),
            "position": position
        }
        await self.node.send(seek)

    async def setVolume(self, volume: int) -> None:
        self._volume = max(min(volume, 1000), 0)
        volume = {
            "op": "volume",
            "guildId": str(self.guild.id),
            "volume": self._volume
        }
        await self.node.send(volume)

    async def destroy(self) -> None:
        destroy = {
            "op": "destroy",
            "guildId": str(self.guild.id)
        }
        await self.node.send(destroy)

    async def setEqualizer(self, eq: Equalizer) -> None:
        if not isinstance(eq, Equalizer):
            return
        self._equalizer = eq
        equalizer = {
            "op": "equalizer",
            "guildId": str(self.guild.id),
            "bands": self._equalizer.eq
        }
        await self.node.send(equalizer)
