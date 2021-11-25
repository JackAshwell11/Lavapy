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

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from .player import Player
    from .pool import Node
    from .tracks import Track

__all__ = ("LavapyEvent",
           "TrackStartEvent",
           "TrackEndEvent",
           "TrackExceptionEvent",
           "TrackStuckEvent",
           "WebsocketOpenEvent",
           "WebsocketClosedEvent")


class LavapyEvent:
    """
    Base Lavapy event. Every event inherits from this.

    If you want to listen to these events, use a :meth:`discord.ext.commands.Bot.listen()`.

    Parameters
    ----------
    event: str
        The event name.
    player: Optional[Player]
        A Lavapy player object.
    """
    def __init__(self, event: str, player: Optional[Player]) -> None:
        self._event: str = event
        self._payload: Dict[str, Any] = {}
        if player is not None:
            self._payload["player"] = player

    def __repr__(self) -> str:
        return f"<Lavapy LavapyEvent (Payload={self.payload})>"

    @property
    def event(self) -> str:
        """Returns the event name."""
        return self._event

    @property
    def payload(self) -> Dict[str, Any]:
        """Returns a dict containing the payload sent to discord.py. This must be parsed to `**kwargs`."""
        return self._payload


class TrackStartEvent(LavapyEvent):
    """
    Fired when a :class:`Track` starts playing. This can be listened to with:

    .. code-block:: python

        @bot.listen()
        async def on_lavapy_track_start(player, track):
            ...

    Parameters
    ----------
    player: Player
        A Lavapy player object.
    track: Track
        A Lavapy track object.
    """
    def __init__(self, player: Player, track: Track) -> None:
        super().__init__("track_start", player)
        self._payload["track"] = track

    def __repr__(self) -> str:
        return f"<Lavapy TrackStartEvent (Payload={self.payload})>"


class TrackEndEvent(LavapyEvent):
    """
    Fired when a :class:`Track` stops playing. This can be listened to with:

    .. code-block:: python

        @bot.listen()
        async def on_lavapy_track_end(player, track, reason):
            ...

    Parameters
    ----------
    player: Player
        A Lavapy player object.
    track: Track
        A Lavapy track object.
    data: Dict[str, Any]
        The raw event data.
    """
    def __init__(self, player: Player, track: Track, data: Dict[str, Any]) -> None:
        super().__init__("track_end", player)
        self._payload["track"] = track
        self._payload["reason"] = data["reason"]

    def __repr__(self) -> str:
        return f"<Lavapy TrackStopEvent (Payload={self.payload})>"


class TrackExceptionEvent(LavapyEvent):
    """
    Fired when a :class:`Track` error has occurred in Lavalink. This can be listened to with:

    .. code-block:: python

        @bot.listen()
        async def on_lavapy_track_exception(player, track, exception):
            ...

    Parameters
    ----------
    player: Player
        A Lavapy player object.
    track: Track
        A Lavapy track object.
    data: Dict[str, Any]
        The raw event data.
    """
    def __init__(self, player: Player, track: Track, data: Dict[str, Any]) -> None:
        super().__init__("track_exception", player)
        self._payload["track"] = track
        if data.get("error"):
            # User is running Lavalink <= 3.3
            self._payload["exception"] = data["error"]
        else:
            # User is running Lavalink >= 3.4
            self._payload["exception"] = data["exception"]

    def __repr__(self) -> str:
        return f"<Lavapy TrackExceptionEvent (Payload={self.payload})>"


class TrackStuckEvent(LavapyEvent):
    """
    Fired when a :class:`Track` is stuck and cannot be played. This can be listened to with:

    .. code-block:: python

        @bot.listen()
        async def on_lavapy_track_stuck(player, track, threshold):
            pass

    Parameters
    ----------
    player: Player
        A Lavapy player object.
    track: Track
        A Lavapy track object.
    data: Dict[str, Any]
        The raw event data.
    """
    def __init__(self, player: Player, track: Track, data: Dict[str, Any]) -> None:
        super().__init__("track_stuck", player)
        self._payload["track"] = track
        self._payload["threshold"] = data["thresholdMs"]

    def __repr__(self) -> str:
        return f"<Lavapy TrackStuckEvent (Payload={self.payload})>"


class WebsocketOpenEvent(LavapyEvent):
    """
    Fired when a websocket connection to a :class:`Node` is open. This can be listened to with:

    .. code-block:: python

        @bot.listen()
        async def on_lavapy_websocket_open(node):
            pass

    Parameters
    ----------
    node: lavapy.pool.Node
        A Lavapy node object.
    """
    def __init__(self, node: Node) -> None:
        super().__init__("websocket_open", None)
        self._payload["node"] = node

    def __repr__(self) -> str:
        return f"<Lavapy WebsocketOpenEvent (Payload={self.payload})>"


class WebsocketClosedEvent(LavapyEvent):
    """
    Fired when a websocket connection to a :class:`Node` is closed. This can be listened to with:

    .. code-block:: python

        @bot.listen()
        async def on_lavapy_websocket_closed(node, reason, code, byRemote):
            pass

    Parameters
    ----------
    node: lavapy.pool.Node
        A Lavapy node object.
    data: Dict[str, Any]
        The raw event data.
    """
    def __init__(self, node: Node, data: Dict[str, Any]) -> None:
        super().__init__("websocket_closed", None)
        self._payload["node"] = node
        self._payload["reason"] = data["reason"]
        self._payload["code"] = data["code"]
        self._payload["byRemote"] = data["byRemote"]

    def __repr__(self) -> str:
        return f"<Lavapy WebsocketClosedEvent (Payload={self.payload})>"
