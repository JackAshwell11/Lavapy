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
from typing import TYPE_CHECKING, Union, Dict, Any

from discord import Client, AutoShardedClient
from discord.ext.commands import Bot, AutoShardedBot

if TYPE_CHECKING:
    from .node import Node

__all__ = ("ClientType",
           "ExponentialBackoff",
           "Stats")

ClientType = Union[Client, AutoShardedClient, Bot, AutoShardedBot]


class ExponentialBackoff:
    """An implementation of the exponential backoff algorithm. This provides an easy
    way to implement an exponential backoff for reconnecting or retrying connections.
    Once instantiated, the delay method will return the next interval to wait for
    when retying a connection. The maximum delay increases exponentially up until
    maxTime using the algorithm base^exponential where base and retry count are
    incremented after each calculation. Then a random value is picked between 0 and
    that calculation. To reset the algorithm, it will need to be redefined overwriting
    the existing variables

    Parameters
    ----------
    base: int
        The base delay in seconds. The first retry will be up to this many seconds
    maxTime: float
        The maximum wait time that can be calculated
    maxTries: int
        The limit to how big the exponential can get. This will affect the sleep time
    """
    def __init__(self, base: int = 1, maxTime: float = 60.0, maxTries: int = 10) -> None:
        self._base: int = base
        self._retries: int = 0
        self._maxTime: float = maxTime
        self._maxTries: int = maxTries

        rand: random.Random = random.Random()
        rand.seed()

        self._random = rand.uniform

    def __repr__(self) -> str:
        return f"<Lavapy ExponentialBackoff (Retries={self._retries}) (Base={self._base})>"

    def delay(self) -> float:
        """
        This implements the exponential backoff algorithm. This is a value between
        0 and base^exp, where after each calculation, the base and retry count is
        incremented.
        """
        exponential = min(self._retries, self._maxTries)
        sleepTime = min(self._random(0, self._base**exponential), self._maxTime)
        self._base += 1
        self._retries += 1
        return sleepTime


class Stats:
    """
    Stores useful information sent by Lavalink about this :class:`Node`.

    Attributes
    ----------
    node: Node
        The Lavapy Node these stats are about.
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
