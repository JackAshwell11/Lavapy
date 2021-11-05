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
from __future__ import annotations

import datetime
import logging
from datetime import datetime, timezone
from typing import Union, Optional, Any, Dict

from discord import VoiceProtocol, VoiceChannel, Guild
from discord.ext.commands import Bot, AutoShardedBot

from .equalizer import Equalizer
from .exceptions import InvalidIdentifier
from .node import Node
from .pool import NodePool
from .tracks import Track
from .queue import Queue

__all__ = ("Player",)

logger = logging.getLogger(__name__)


class Player(VoiceProtocol):
    """
    Lavapy Player object. This subclasses :class:`discord.VoiceProtocol` and such should be treated as one with additions.

    Examples
    --------
    .. code-block:: python

       @commands.command()
       async def connect(self, channel: discord.VoiceChannel):
           voice_client = await channel.connect(cls=lavapy.Player)

    .. warning::
        This class should not be created manually but can be subclassed to add additional functionality. You should instead use :meth:`discord.VoiceChannel.connect()` and pass the player object to the cls kwarg.

    Parameters
    ----------
    bot: Union[Bot, AutoShardedBot]
        The discord.py Bot or AutoShardedBot.
    channel: VoiceChannel
        A discord.py VoiceChannel for the player to connect to.

    Attributes
    ----------
    bot: Union[Bot, AutoShardedBot]
        The discord.py Bot or AutoShardedBot.
    channel: VoiceChannel
        A discord.py VoiceChannel for the player to connect to.
    node: Optional[Node]
        The Lavapy Node object which is used for communicating with Lavalink.
    track: Optional[Track]
        The currently playing track.
    volume: int
        The volume the player should play at.
    equalizer: Equalizer
        The currently applied Equalizer.
    queue: Queue
        A Queue object which can be used to line up tracks and retrieve them.
    """
    def __init__(self, bot: Union[Bot, AutoShardedBot], channel: VoiceChannel) -> None:
        super().__init__(bot, channel)
        self.bot: Union[Bot, AutoShardedBot] = bot
        self.channel: VoiceChannel = channel
        self.node: Optional[Node] = NodePool.getNode()
        self.track: Optional[Track] = None
        self.volume: int = 100
        self.equalizer: Equalizer = Equalizer.flat()
        self.queue: Queue = Queue()
        self._voiceState: Dict[str, Any] = {}
        self._connected: bool = False
        self._paused: bool = False
        self._lastUpdateTime: Optional[datetime.datetime] = None
        self._lastPosition: Optional[float] = None

    def __repr__(self) -> str:
        return f"<Lavapy Player (ChannelID={self.channel.id}) (GuildID={self.guild.id})>"

    @property
    def guild(self) -> Guild:
        """Returns the :class:`discord.Guild`: this player is in."""
        return self.channel.guild

    @property
    def position(self) -> float:
        """The current position of the track in seconds. If nothing is playing, this returns 0."""
        if not self.isPlaying:
            return 0

        if self.isPaused:
            return min(self._lastPosition, self.track.length)

        timeSinceLastUpdate = (datetime.datetime.now(timezone.utc) - self._lastUpdateTime).total_seconds()
        return min(self._lastPosition + timeSinceLastUpdate, self.track.length)

    @property
    def isConnected(self) -> bool:
        """Returns whether the player is connected to a channel."""
        return self._connected

    @property
    def isPlaying(self) -> bool:
        """Returns whether the player is currently playing a track."""
        return self.isConnected and self.track is not None

    @property
    def isPaused(self) -> bool:
        """Returns whether the player is currently paused."""
        return self._paused

    def updateState(self, state: Dict[str, Any]) -> None:
        """
        Stores the last update time and the last position.

        Parameters
        ----------
        state: Dict[str, Any]
            The raw info sent by Lavalink.
        """
        # State updates are sent in milliseconds so need to be converted to seconds (/1000)
        state: Dict[str, Any] = state.get("state")
        self._lastUpdateTime = datetime.fromtimestamp(state.get("time")/1000, timezone.utc)

        self._lastPosition = state.get("position", 0)/1000

    async def on_voice_server_update(self, data: Dict[str, str]) -> None:
        """|coro|

        Called when the bot connects to a voice channel.

        Parameters
        ----------
        data: Dict[str, str]
            The raw info sent by Discord about the voice channel.
        """
        self._voiceState.update({"event": data})
        await self.sendVoiceUpdate()

    async def on_voice_state_update(self, data: Dict[str, Any]) -> None:
        """|coro|

        Called when the bot's voice state changes.

        Parameters
        ----------
        data: Dict[str, Any]
            The raw info sent by Discord about the bot's voice state.
        """
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
        """|coro|

        Sends data collected from on_voice_server_update and on_voice_state_update to Lavalink.
        """
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
        """|coro|

        Connects the player to a voice channel.

        Parameters
        ----------
        timeout: float
            The timeout for the connection.
        reconnect: bool
            A bool stating if reconnection is expected.
        """
        await self.guild.change_voice_state(channel=self.channel)
        self.node.players.append(self)
        self._connected = True

        logger.info(f"Connected to voice channel: {self.channel.id}")

    async def disconnect(self, *, force: bool = False) -> None:
        """|coro|

        Disconnects the player from a voice channel.

        Parameters
        ----------
        force: bool
            Whether to force the disconnection. This is currently not used.
        """
        await self.guild.change_voice_state(channel=None)
        self.node.players.remove(self)
        self._connected = False

        logger.info(f"Disconnected from voice channel: {self.channel.id}")

    async def play(self, track: Track, startTime: int = 0, endTime: int = 0, volume: int = 100, replace: bool = True, pause: bool = False) -> None:
        """|coro|

        Plays a given track.

        Parameters
        ----------
        track: Track
            The track to play.
        startTime: int
            The position in milliseconds to start at. By default, this is the beginning.
        endTime: int
            The position in milliseconds to end at. By default, this is the end.
        volume: int
            The volume at which the player should play the track at. By default, this is 100.
        replace: bool
            A bool stating if the current track should be replaced or not. By default, this is True.
        pause: bool
            A bool stating if the track should start paused. By default, this is False.
        """
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
        """|coro|

        Stops the currently playing track.
        """
        stop = {
            "op": "stop",
            "guildId": str(self.guild.id)
        }
        tempTrack = self.track
        self.track = None
        await self.node.send(stop)

        logger.debug(f"Stopped playing track: {tempTrack.title} in {self.channel.id}")

    async def pause(self) -> None:
        """|coro|

        Pauses the player if it was playing.
        """
        await self._togglePause(True)

    async def resume(self) -> None:
        """|coro|

        Resumes the player if it was paused.
        """
        await self._togglePause(False)

    async def _togglePause(self, pause: bool) -> None:
        """|coro|

        Toggles the player's pause state.

        Parameters
        ----------
        pause: bool
            A bool stating whether the player's paused state should be True or False.
        """
        pause = {
            "op": "pause",
            "guildId": str(self.guild.id),
            "pause": pause
        }
        self._paused = pause
        await self.node.send(pause)

        logger.debug(f"Toggled pause: {pause} in {self.channel.id}")

    async def seek(self, position: int) -> None:
        """|coro|

        Seek to a given position.

        Parameters
        ----------
        position: int
            The position to seek to.
        """
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
        """|coro|

        Changes the player's volume.

        Parameters
        ----------
        volume: int
            The new player volume.
        """
        self.volume = max(min(volume, 1000), 0)
        volume = {
            "op": "volume",
            "guildId": str(self.guild.id),
            "volume": self.volume
        }
        await self.node.send(volume)

        logger.debug(f"Set volume to: {volume}")

    async def moveTo(self, channel: VoiceChannel) -> None:
        """|coro|

        Moves the player to another :class:`discord.VoiceChannel`.

        Parameters
        ----------
        channel: VoiceChannel
            The voice channel to move to.
        """
        await self.guild.change_voice_state(channel=channel)

    async def setEqualizer(self, eq: Equalizer) -> None:
        """|coro|

        Sets the player's Equalizer.

        Parameters
        ----------
        eq: Equalizer
            The Equalizer to change to.
        """
        if not isinstance(eq, Equalizer):
            return
        self.equalizer = eq
        equalizer = {
            "op": "equalizer",
            "guildId": str(self.guild.id),
            "bands": self.equalizer.eq
        }
        await self.node.send(equalizer)

        logger.debug(f"Changed equalizer to: {self.equalizer}")

# async def destroy(self) -> None:
#     destroy = {
#         "op": "destroy",
#         "guildId": str(self.guild.id)
#     }
#     await self.node.send(destroy)
