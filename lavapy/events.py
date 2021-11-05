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

from typing import Dict, Tuple

from .tracks import Track

__all__ = ("LavapyEvent",
           "TrackStartEvent",
           "TrackEndEvent",
           "TrackExceptionEvent",
           "TrackStuckEvent",
           "WebsocketClosedEvent")


class LavapyEvent:
    """
    Base Lavapy event. Every event inherits from this.

    If you want to listen to these events, use a :class:`discord.ext.commands.Bot.listen()`:

    .. code-block:: python

        @bot.listen
        async def onLavapyTrackStart(self, DO):
            ...code

    Attributes
    ----------
    event: str
        The event name which has been dispatched.
    """
    def __init__(self, event: str) -> None:
        self.event = event

    def __repr__(self) -> str:
        return f"<Lavapy LavapyEvent (Event={self.event})>"

    @property
    def listenerArgs(self) -> None:
        """Returns the arguments sent to :class:`discord.ext.commands.Bot.listen()`."""
        return None


class TrackStartEvent(LavapyEvent):
    """
    Fired when a track starts playing.

    Attributes
    ----------
    track: Track
        A Lavapy Track object.
    """
    def __init__(self, track: Track) -> None:
        super().__init__("track_start")
        self.track = track

    def __repr__(self) -> str:
        return f"<Lavapy TrackStartEvent (Track={self.track.identifier})>"

    @property
    def listenerArgs(self) -> Track:
        """Returns the arguments sent to :class:`discord.ext.commands.Bot.listen()`."""
        return self.track


class TrackEndEvent(LavapyEvent):
    """
    Fired when a track stops playing.

    Attributes
    ----------
    track: Track
        A Lavapy Track object.
    reason: str
        The reason the track stopped playing.
    """
    def __init__(self, track: Track, reason: str) -> None:
        super().__init__("track_end")
        self.track = track
        self.reason = reason

    def __repr__(self) -> str:
        return f"<Lavapy TrackStopEvent (Track={self.track.identifier}) (Reason={self.reason})>"

    @property
    def listenerArgs(self) -> Tuple[Track, str]:
        """Returns the arguments sent to :class:`discord.ext.commands.Bot.listen()`."""
        return self.track, self.reason


class TrackExceptionEvent(LavapyEvent):
    """
    Fired when a track error has occurred in Lavalink.

    Attributes
    ----------
    track: Track
        A Lavapy Track object.
    exception: str
        The exception that occurred in Lavalink.
    """
    def __init__(self, track: Track, exception: Dict[str, str]) -> None:
        super().__init__("track_exception")
        self.track = track
        if exception.get("error"):
            # User is running Lavalink <= 3.3
            self.exception = exception["error"]
        else:
            # User is running Lavalink >= 3.4
            self.exception = exception["exception"]

    def __repr__(self) -> str:
        return f"<Lavapy TrackExceptionEvent (Track={self.track.identifier}) (Exception={self.exception})>"

    @property
    def listenerArgs(self) -> Tuple[Track, str]:
        """Returns the arguments sent to :class:`discord.ext.commands.Bot.listen()`."""
        return self.track, self.exception


class TrackStuckEvent(LavapyEvent):
    """
    Fired when a track is stuck and cannot be played.

    Attributes
    ----------
    track: Track
        A Lavapy Track object.
    threshold: str
        The exception that occurred in Lavalink.
    """
    def __init__(self, track: Track, threshold: int) -> None:
        super().__init__("track_stuck")
        self.track = track
        self.threshold = threshold

    def __repr__(self) -> str:
        return f"<Lavapy TrackStuckEvent (Track={self.track.identifier}) (Threshold={self.threshold})>"

    @property
    def listenerArgs(self) -> Tuple[Track, int]:
        """Returns the arguments sent to :class:`discord.ext.commands.Bot.listen()`."""
        return self.track, self.threshold


class WebsocketClosedEvent(LavapyEvent):
    """
    Fired when a websocket connection to a node is closed.

    Attributes
    ----------
    reason: str
        The reason the websocket was closed.
    code: int
        The discord error code that was sent.
    byRemote: bool
        A bool stating if the connection was closed remotely or not.
    """
    def __init__(self, reason: str, code: int, byRemote: bool) -> None:
        super().__init__("websocket_closed")
        self.reason = reason
        self.code = code
        self.byRemote = byRemote

    def __repr__(self) -> str:
        return f"<Lavapy WebsocketClosedEvent (Reason={self.reason}) (Code={self.code}) (ByRemote={self.byRemote})>"

    @property
    def listenerArgs(self) -> Tuple[str, int, bool]:
        """Returns the arguments sent to :class:`discord.ext.commands.Bot.listen()`."""
        return self.reason, self.code, self.byRemote
