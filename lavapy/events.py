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

from typing import Dict

from .tracks import Track

__all__ = ("LavapyEvent",
           "TrackEvent",
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
    """
    def __init__(self, event: str):
        self.event = event


class TrackEvent(LavapyEvent):
    """Base Lavapy event for all track events."""
    def __init__(self, event: str, track: Track):
        super().__init__(event)
        self.track = track


class TrackStartEvent(TrackEvent):
    """Sent when a track starts playing."""


class TrackEndEvent(TrackEvent):
    """Sent when a track ends playing."""
    def __init__(self, event: str, track: Track, reason: str):
        super().__init__(event, track)
        self.reason = reason


class TrackExceptionEvent(TrackEvent):
    """Sent when a track exception occurs in Lavalink."""
    def __init__(self, event: str, track: Track, exception: Dict[str, str]):
        super().__init__(event, track)
        self.exception = exception


class TrackStuckEvent(TrackEvent):
    """Sent when a track stuck occurs in Lavalink."""


class WebsocketClosedEvent(LavapyEvent):
    """"""
