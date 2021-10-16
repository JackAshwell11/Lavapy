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
from typing import Union, List

from discord import VoiceProtocol, VoiceChannel
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
        self.volume = 100
        self._voiceState = {}
        self._track = None
        self._connected = False
        self._paused = False
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
