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

from typing import TYPE_CHECKING, Union, List

from .exceptions import QueueEmpty
from .tracks import MultiTrack

if TYPE_CHECKING:
    from .tracks import Track


__all__ = ("Queue",)


class Queue:
    """
    A class representing a usable Queue.
    """
    def __init__(self) -> None:
        self._queue: List[Track] = []

    def __repr__(self) -> str:
        return f"<Lavapy Queue (Queue={self._queue})>"

    @property
    def queue(self) -> List[Track]:
        """Returns a list of :class:`Track` objects."""
        return self._queue

    @property
    def count(self) -> int:
        """Returns the size of the :class:`Queue`."""
        return len(self._queue)

    @property
    def isEmpty(self) -> bool:
        """Returns whether the :class:`Queue` is empty or not."""
        return not self._queue

    def get(self) -> Track:
        """
        Gets the next :class:`Track` in the :class:`Queue`.

        Raises
        ------
        QueueEmpty
            The current :class:`Queue` is empty.

        Returns
        -------
        Track
            The next :class:`Track` in the :class:`Queue`.
        """
        if self.isEmpty:
            raise QueueEmpty("Queue is empty")
        return self._queue.pop()

    def add(self, track: Track) -> None:
        """
        Adds a :class:`Track` to the :class:`Queue`.

        Parameters
        ----------
        track: Track
            The :class:`Track` to add to the :class:`Queue`.
        """
        self._queue.append(track)

    def addIterable(self, iterable: Union[MultiTrack, List[Track]]) -> None:
        """
        Adds an iterable to the :class:`Queue`.

        Parameters
        ----------
        iterable: Union[MultiTrack, List[Track]]
            The iterable to add to the queue.
        """
        if isinstance(iterable, MultiTrack):
            iterable = iterable.tracks
        for track in iterable:
            self.add(track)

    def clear(self) -> None:
        """Clears all :class`Track` objects in the :class:`Queue`."""
        self.queue.clear()
