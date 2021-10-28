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
from datetime import datetime, timezone
import datetime
from typing import Union, List, Optional, Any, Dict

from discord import VoiceProtocol, VoiceChannel, Guild
from discord.ext.commands import Bot, AutoShardedBot

from .equalizer import Equalizer
from .exceptions import InvalidIdentifier
from .pool import getNode
from .tracks import Track, Playlist
from .node import Node

__all__ = ("Player",)

logger = logging.getLogger(__name__)


class Player(VoiceProtocol):
    def __init__(self, bot: Union[Bot, AutoShardedBot], channel: VoiceChannel) -> None:
        super().__init__(bot, channel)
        self.bot: Union[Bot, AutoShardedBot] = bot
        self.channel: VoiceChannel = channel
        self.node: Optional[Node] = getNode()
        self.track: Optional[Track] = None
        self.volume: int = 100
        self._voiceState: Dict[str, Any] = {}
        self._connected: bool = False
        self._paused: bool = False
        self._lastUpdateTime: Optional[datetime.datetime] = None
        self._lastPosition: Optional[float] = None
        self._equalizer: Equalizer = Equalizer.flat()

    def __repr__(self) -> str:
        return f"<Lavapy Player (ChannelID={self.channel.id}) (GuildID={self.guild.id})>"

    @property
    def guild(self) -> Guild:
        return self.channel.guild

    @property
    def position(self) -> float:
        if not self.isPlaying:
            return 0

        if self.isPaused:
            return min(self._lastPosition, self.track.length)

        timeSinceLastUpdate = (datetime.datetime.now(timezone.utc) - self._lastUpdateTime).total_seconds()
        return min(self._lastPosition + timeSinceLastUpdate, self.track.length)

    @property
    def isConnected(self) -> bool:
        return self._connected

    @property
    def isPlaying(self) -> bool:
        return self.isConnected and self.track is not None

    @property
    def isPaused(self) -> bool:
        return self._paused

    def updateState(self, state: Dict[str, Any]):
        # State updates are sent in milliseconds so need to be converted to seconds (/1000)
        state: Dict[str, Any] = state.get("state")
        self._lastUpdateTime = datetime.datetime.fromtimestamp(state.get("time")/1000, timezone.utc)

        self._lastPosition = state.get("position", 0)/1000

    async def on_voice_server_update(self, data: dict) -> None:
        self._voiceState.update({"event": data})
        await self.sendVoiceUpdate()

    async def on_voice_state_update(self, data: dict) -> None:
        self._voiceState.update({"sessionId": data["session_id"]})

        channelID = data["channel_id"]
        if channelID is None:
            # Disconnecting
            self._voiceState.clear()
            return

        channel = self.bot.get_channel(channelID)
        if channel != self.channel:
            logger.debug(f"Moved player to channel: {channel.id}")
            self.channel = channel

        await self.sendVoiceUpdate()

    async def sendVoiceUpdate(self) -> None:
        if {"sessionId", "event"} == self._voiceState.keys():
            logger.debug(f"Dispatching voice update: {self.channel.id}")

            voiceUpdate = {
                "op": "voiceUpdate",
                "guildId": str(self.guild.id),
                "sessionId": self._voiceState["sessionId"],
                "event": self._voiceState["event"]
            }
            await self.node.send(voiceUpdate)

    async def connect(self, timeout: float, reconnect: bool) -> None:
        await self.guild.change_voice_state(channel=self.channel)
        self.node.players.append(self)
        self._connected = True

        logger.info(f"Connected to voice channel: {self.channel.id}")

    async def disconnect(self, *, force: bool = False) -> None:
        await self.guild.change_voice_state(channel=None)
        self.node.players.remove(self)
        self._connected = False

        logger.info(f"Disconnected from voice channel: {self.channel.id}")

    async def getYoutubeTracks(self, query: str) -> List[Optional[Track]]:
        logger.info(f"Getting Youtube tracks with query: {query}")

        return await self._getTracks(f"ytsearch:{query}")

    async def getSoundcloudTracks(self, query: str) -> List[Optional[Track]]:
        logger.info(f"Getting Soundcloud tracks with query: {query}")

        return await self._getTracks(f"scsearch:{query}")

    async def _getTracks(self, query: str) -> List[Optional[Track]]:
        songs = await self.node.getData(query)
        return [Track(element.get("track"), element.get("info")) for element in songs.get("tracks")] if songs.get("loadType") != "NO_MATCHES" else []

    # TODO: Playlist need more work
    # async def getYoutubePlaylist(self, query: str) -> Optional[Playlist]:
    #     logger.info(f"Getting Youtube playlist with query: {query}")
    #
    #     return await self._getPlaylist(f"ytsearch:{query}")
    #
    # async def getSoundcloudPlaylist(self, query: str) -> Optional[Playlist]:
    #     logger.info(f"Getting Soundcloud playlist with query: {query}")
    #
    #     return await self._getPlaylist(f"scsearch:{query}")
    #
    # async def _getPlaylist(self, query: str) -> Optional[Playlist]:
    #     songs = await self.node.getData(query)
    #     return Playlist(songs.get("playlistInfo").get("name"), songs.get("tracks")) if songs.get("loadType") != "NO_MATCHES" else None

    async def play(self, track: Track, startTime: int = 0, endTime: int = 0, volume: int = 100, replace: bool = True, pause: bool = False) -> None:
        if self.isPlaying and not replace:
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
        self.track = track
        self.volume = volume
        await self.node.send(newTrack)

        logger.debug(f"Started playing track: {self.track.title} in {self.channel.id}")

    async def stop(self) -> None:
        stop = {
            "op": "stop",
            "guildId": str(self.guild.id)
        }
        tempTrack = self.track
        self.track = None
        await self.node.send(stop)

        logger.debug(f"Stopped playing track: {tempTrack.title} in {self.channel.id}")

    async def pause(self) -> None:
        await self._togglePause(True)

    async def resume(self) -> None:
        await self._togglePause(False)

    async def _togglePause(self, pause: bool) -> None:
        pause = {
            "op": "pause",
            "guildId": str(self.guild.id),
            "pause": pause
        }
        self._paused = pause
        await self.node.send(pause)

        logger.debug(f"Toggled pause: {pause} in {self.channel.id}")

    async def seek(self, position: int) -> None:
        if position > self.track.length:
            raise InvalidIdentifier("Seek position is bigger than track length")
        seek = {
            "op": "seek",
            "guildId": str(self.guild.id),
            "position": position
        }
        await self.node.send(seek)

        logger.debug(f"Seeked to position: {position}")

    async def setVolume(self, volume: int) -> None:
        self.volume = max(min(volume, 1000), 0)
        volume = {
            "op": "volume",
            "guildId": str(self.guild.id),
            "volume": self.volume
        }
        await self.node.send(volume)

        logger.debug(f"Set volume to: {volume}")

    async def moveTo(self, channel: VoiceChannel) -> None:
        await self.guild.change_voice_state(channel=channel)

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

        logger.debug(f"Changed equalizer to: {self._equalizer}")

    # async def destroy(self) -> None:
    #     destroy = {
    #         "op": "destroy",
    #         "guildId": str(self.guild.id)
    #     }
    #     await self.node.send(destroy)
