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

from typing import List, Tuple, Dict, Union

__all__ = ("Equalizer",)


class Equalizer:
    """
    A class representing a usable Equalizer.

    Attributes
    ---------
    levels: List[Tuple[int, float]]
        A list of tuple pairs containing a band int and gain float.
    name: str
        A string to name this Equalizer.
    eq: List[Dict[str, Union[int, float]]]
        A list of {'band': int, 'gain': float} pairs.
    """

    def __init__(self, levels: List[Tuple[int, float]], name: str) -> None:
        self.levels: List[Tuple[int, float]] = levels
        self.name: str = name
        self.eq: List[Dict[str, Union[int, float]]] = self._setup(levels)

    def __repr__(self) -> str:
        return f"<Lavapy Equalizer (Name={self.name}) (Levels={self.levels})>"

    @staticmethod
    def _setup(levels: List[Tuple[int, float]]) -> List[Dict[str, Union[int, float]]]:
        """
        A function to convert self.levels into a dict for sending to Lavalink.

        Parameters
        ----------
        levels: List[Tuple[int, float]]
            A list of tuple pairs containing a band int and gain float.

        Returns
        -------
        List[Dict[str, Union[int, float]]]
            A list of {'band': int, 'gain': float} pairs.
        """
        return [{"band": level[0], "gain": level[1]} for level in levels]

    @classmethod
    def build(cls, levels: List[Tuple[int, float]], name: str = "CustomEqualizer") -> Equalizer:
        """
        Build a custom Equalizer class with the given levels.

        Parameters
        ----------
        levels: List[Tuple[int, float]]
            A custom list of tuple pairs containing a band int and gain float. You will have to construct this yourself.
        name: str
            An optional string to name this Equalizer. If this is not supplied, it will be set to 'CustomEqualizer'.

        Returns
        -------
        Equalizer
            A custom Equalizer object.
        """
        return cls(levels, name)

    @classmethod
    def flat(cls):
        """
        A Flat Equalizer. This will not provide a cut or boost to any frequency.

        This is the default EQ for :class:`Player`.

        Returns
        -------
        Equalizer
            A Flat Equalizer object.
        """
        levels = [(0, 0.0), (1, 0.0), (2, 0.0), (3, 0.0), (4, 0.0),
                  (5, 0.0), (6, 0.0), (7, 0.0), (8, 0.0), (9, 0.0),
                  (10, 0.0), (11, 0.0), (12, 0.0), (13, 0.0), (14, 0.0)]
        return cls(levels, "Flat")
