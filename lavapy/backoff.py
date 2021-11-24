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

__all__ = ("ExponentialBackoff",)


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