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

import random
from typing import TYPE_CHECKING, Iterable, Union, List, Dict, Any

from .exceptions import QueueEmpty
from .tracks import MultiTrack

if TYPE_CHECKING:
    from .node import Node
    from .tracks import Track

__all__ = ("ExponentialBackoff",
           "Queue",
           "Stats")


class ExponentialBackoff:
    """
    An implementation of the exponential backoff algorithm. This provides a convenient interface to implement an
    exponential backoff for reconnecting or retrying transmissions in a distributed network. Once instantiated,
    the delay method will return the next interval to wait for when retrying a connection or transmission.

    Parameters
    ----------
    base: int
        The base delay in seconds. Changing this changes how fast the delay increases.
    maxRetries: int
        The maximum amount of retries allowed. Changing this changes how big the delay can get.
    """
    def __init__(self, base: int = 1, maxRetries: int = 20) -> None:
        self._base: int = base
        self._maxRetries: int = maxRetries

        self._retries: int = 0

        rand = random.Random()
        rand.seed()

        self._rand = rand.uniform

    def __repr__(self) -> str:
        return f"<Lavapy ExponentialBackoff (Base={self.base}) (Retries={self.retries}) (MaxRetries={self.maxRetries})>"

    @property
    def base(self) -> int:
        """Returns the base on the equation."""
        return self._base

    @property
    def retries(self) -> int:
        """Returns the amount of current retries."""
        return self._retries

    @property
    def maxRetries(self) -> int:
        """Returns the max amount of retries."""
        return self._maxRetries

    def delay(self) -> float:
        """
        Computes the next delay. This is a value between 0 and (base*2)^(retries+1) where if the amount of retries
        currently done is bigger than maxRetries, then retries resets.
        """
        self._retries += 1

        if self._retries > self._maxRetries:
            self._retries = 1

        return self._rand(0, self._base * 2 ** self._retries)


class Queue:
    """
    A class representing a usable Queue.
    """
    def __init__(self) -> None:
        self._tracks: List[Track] = []

    def __repr__(self) -> str:
        return f"<Lavapy Queue (Queue={self._tracks})>"

    @property
    def tracks(self) -> List[Track]:
        """Returns a list of track objects."""
        return self._tracks

    @property
    def count(self) -> int:
        """Returns the size of the queue."""
        return len(self._tracks)

    @property
    def isEmpty(self) -> bool:
        """Returns whether the queue is empty or not."""
        return not self._tracks

    def get(self) -> Track:
        """
        Gets the next :class:`Track` in the queue.

        Raises
        ------
        QueueEmpty
            The current queue is empty.

        Returns
        -------
        Track
            The next track in the queue.
        """
        if self.isEmpty:
            raise QueueEmpty("Queue is empty")
        return self._tracks.pop()

    def add(self, track: Track) -> None:
        """
        Adds a :class:`Track` to the queue.

        Parameters
        ----------
        track: Track
            The track to add to the queue.
        """
        self._tracks.append(track)

    def addIterable(self, iterable: Union[MultiTrack, Iterable[Track]]) -> None:
        """
        Adds an iterable to the :class:`Queue`.

        Parameters
        ----------
        iterable: Union[MultiTrack, Iterable[Track]]
            The iterable to add to the queue.
        """
        if isinstance(iterable, MultiTrack):
            iterable = iterable.tracks
        for track in iterable:
            self.add(track)

    def clear(self) -> None:
        """Clears all track objects in the queue."""
        self.queue.clear()


class Stats:
    """
    Stores useful information sent by Lavalink about this :class:`Node`.

    Attributes
    ----------
    node: Node
        The Lavapy node these stats are about.
    uptime: int
        How long this node has been up for.
    players: int
        How many players are connected to this node.
    playingPlayers: int
        How many players that are connected to this node are playing tracks.
    memoryReservable: int
        How much memory is reserved by the system.
    memoryUsed: int
        How much memory is used by the system.
    memoryFree: int
        How much memory is free in the system.
    memoryAllocated: int
        How much memory is allocated to Lavalink.
    cpuCores: int
        How many cpu cores the system has.
    systemLoad: float
        The load on the system as a percentage.
    lavalinkLoad: float
        The load on the Lavalink server as a percentage.
    framesSent: int
        How many frames have been sent to Lavalink by this node.
    framesDeficit: int
        How many frames have been lost that were sent by this node.
    framesNulled: int
        How many frames have errored that were sent by this node.
    """
    def __init__(self, node: Node, data: Dict[str, Any]) -> None:
        self.node: Node = node
        self.uptime: int = data["uptime"]
        self.players: int = data["players"]
        self.playingPlayers: int = data["playingPlayers"]

        memory: Dict[str, Any] = data["memory"]
        self.memoryReservable: int = memory["reservable"]
        self.memoryUsed: int = memory["used"]
        self.memoryFree: int = memory["free"]
        self.memoryAllocated: int = memory["allocated"]

        cpu: Dict[str, Any] = data["cpu"]
        self.cpuCores: int = cpu["cores"]
        self.systemLoad: float = cpu["systemLoad"]
        self.lavalinkLoad: float = cpu["lavalinkLoad"]

        frameStats: Dict[str, Any] = data.get("frameStats", {})
        self.framesSent: int = frameStats.get("sent", -1)
        self.framesDeficit: int = frameStats.get("deficit", -1)
        self.framesNulled: int = frameStats.get("nulled", -1)

    def __repr__(self) -> str:
        return f"<Lavapy Stats (Node={self.node})>"
