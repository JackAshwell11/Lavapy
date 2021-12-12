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
from typing import TYPE_CHECKING, Iterable, List, Union

from .exceptions import QueueEmpty, RepeatException
from .tracks import MultiTrack

if TYPE_CHECKING:
    from .player import Player
    from .tracks import Track

__all__ = ("Queue",)


class Queue:
    """
    A class representing a usable Queue.
    """
    def __init__(self, player: Player) -> None:
        self._player: Player = player
        self._tracks: List[Track] = []
        self._currentTrack: int = -1

    def __repr__(self) -> str:
        return f"<Lavapy Queue (Queue={self._tracks})>"

    @property
    def tracks(self) -> List[Track]:
        """Returns a list of track objects."""
        return self._tracks

    @property
    def currentTrack(self) -> int:
        """Returns the current position in the queue."""
        return self._currentTrack

    @property
    def count(self) -> int:
        """Returns the size of the queue."""
        return len(self._tracks)

    @property
    def isEmpty(self) -> bool:
        """Returns whether the queue is empty or not."""
        return self.currentTrack == self.count-1

    def next(self) -> Track:
        """
        Gets the next :class:`Track` in the queue.

        Raises
        ------
        QueueEmpty
            The current queue is empty.
        RepeatException
            Cannot get next track if player is repeating

        Returns
        -------
        Track
            The next track in the queue.
        """
        if self.isEmpty:
            raise QueueEmpty("Queue is empty")
        if self._player.isRepeating:
            raise RepeatException("Cannot get next track if player is repeating")
        self._currentTrack += 1
        return self.tracks[self.currentTrack]

    def previous(self) -> Track:
        """
        Gets the previous :class:`Track` in the queue.

        Raises
        ------
        QueueEmpty
            The current queue is empty.
        RepeatException
            Cannot get previous track if player is repeating

        Returns
        -------
        Track
            The previous track in the queue.
        """
        if self.currentTrack == 0:
            raise QueueEmpty("Queue is empty")
        if self._player.isRepeating:
            raise RepeatException("Cannot get previous track if player is repeating")
        self._currentTrack -= 1
        return self.tracks[self.currentTrack]


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

    def reset(self) -> None:
        """Resets the queue."""
        self.tracks.clear()
        self._currentTrack = 0

    def shuffle(self) -> None:
        """Shuffles the queue but keeps the currently playing track in the same place."""
        tempTrack = self.tracks.pop(self.currentTrack)
        random.shuffle(self.tracks)
        self.tracks.insert(self.currentTrack, tempTrack)
