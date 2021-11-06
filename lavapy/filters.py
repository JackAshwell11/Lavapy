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

from enum import Enum
from typing import List, Tuple, Dict, Union, Any

from .exceptions import InvalidFilterArgument

__all__ = ("FilterName",
           "LavapyFilter",
           "Equalizer",
           "Karaoke",
           "Timescale",
           "Tremolo",
           "Vibrato",
           "Rotation",
           "Distortion",
           "ChannelMix",
           "LowPass")


class FilterName(Enum):
    """Stores all the names of each :class:`LavapyFilter`."""
    Equalizer = "equalizer"
    Karaoke = "karaoke"
    Timescale = "timescale"
    Tremolo = "tremolo"
    Vibrato = "vibrato"
    Rotation = "rotation"
    Distortion = "distortion"
    ChannelMix = "channelMix"
    LowPass = "lowPass"


class LavapyFilter:
    """
    Base Lavapy Filter. Event filters inherit from this.

    Attributes
    ----------
    name: str
        The filter's name.
    """
    def __init__(self, name: FilterName):
        self.name: str = name.value
        self._payload: Any = {}

    def __repr__(self) -> str:
        return f"<Lavapy Filter (Payload={self._payload})>"


class Equalizer(LavapyFilter):
    """
    A class representing a usable Equalizer.

    Attributes
    ---------
    levels: List[Tuple[int, float]]
        A list of tuple pairs containing a band int and gain float.
    name: str
        A string to name this Equalizer.
    """

    def __init__(self, levels: List[Tuple[int, float]], name: str) -> None:
        super().__init__(FilterName.Equalizer)
        self.levels: List[Tuple[int, float]] = levels
        self.name: str = name
        self._payload: List[Dict[str, Union[int, float]]] = self._setup(levels)

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
    def flat(cls) -> Equalizer:
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


class Karaoke(LavapyFilter):
    """
    Simulates an :class:`Equalizer` which specifically targets removing vocals.

    Attributes
    ----------
    level: float
        to do. This defaults to 1.0.
    monoLevel: float
        to do. This defaults to 1.0.
    filterBand: float
        to do. This defaults to 220.0.
    filterWidth: float
        to do. This defaults to 100.0.
    """
    def __init__(self, level: float = 1.0, monoLevel: float = 1.0, filterBand: float = 220.0, filterWidth: float = 100.0) -> None:
        super().__init__(FilterName.Karaoke)
        self.level = self._payload["level"] = level
        self.monoLevel = self._payload["monoLevel"] = monoLevel
        self.filterBand = self._payload["filterBand"] = filterBand
        self.filterWidth = self._payload["filterWidth"] = filterWidth

    def __repr__(self) -> str:
        return f"<Lavapy KaraokeFilter (Payload={self._payload})>"


class Timescale(LavapyFilter):
    """
    Changes the sped, pitch and rate of a track.

    Attributes
    ----------
    speed: float
        to do. This defaults to 1.0.
    pitch: float
        to do. This defaults to 1.0.
    rate: float
        to do.. This defaults to 1.0.
    """
    def __init__(self, speed: float = 1.0, pitch: float = 1.0, rate: float = 1.0) -> None:
        super().__init__(FilterName.Timescale)
        self.speed = self._payload["speed"] = speed
        self.pitch = self._payload["pitch"] = pitch
        self.rate = self._payload["rate"] = rate

    def __repr__(self) -> str:
        return f"<Lavapy TimescaleFilter (Payload={self._payload})>"


class Tremolo(LavapyFilter):
    """
    Uses amplification to create a shuddering effect, where the volume quickly oscillates.

    Here is an `Example <https://en.wikipedia.org/wiki/File:Fuse_Electronics_Tremolo_MK-III_Quick_Demo.ogv>`_.

    Attributes
    ----------
    frequency: float
        to do. This must be bigger than 0. This defaults to 2.0.
    depth: float
        to do. This must be between 0 and 1. This defaults to 0.5.

    Raises
    ------
    InvalidFilterArgument
        An invalid filter argument has been passed.
    """
    def __init__(self, frequency: float = 2.0, depth: float = 0.5) -> None:
        super().__init__(FilterName.Tremolo)
        if frequency < 0.0:
            raise InvalidFilterArgument("Frequency must be more than 0.")
        if depth < 0.0 or depth > 1.0:
            raise InvalidFilterArgument("Depth must be between 0 and 1.")
        self.frequency = self._payload["frequency"] = frequency
        self.depth = self._payload["depth"] = depth

    def __repr__(self) -> str:
        return f"<Lavapy TremoloFilter (Payload={self._payload})>"


class Vibrato(LavapyFilter):
    """
    Similar to :class:`Tremolo` but oscillates the pitch instead of the volume.

    Attributes
    ----------
    frequency: float
        to do. This must be between 0 and 14. This defaults to 2.0.
    depth: float
        to do. This must be between 0 and 1. This defaults to 0.5.

    Raises
    ------
    InvalidFilterArgument
        An invalid filter argument has been passed.
    """
    def __init__(self, frequency: float = 2.0, depth: float = 0.5) -> None:
        super().__init__(FilterName.Vibrato)
        if frequency < 0.0 or frequency > 14.0:
            raise InvalidFilterArgument("Frequency must be between 0 and 14.")
        if depth < 0.0 or depth > 1.0:
            raise InvalidFilterArgument("Depth must be between 0 and 1.")
        self.frequency = self._payload["frequency"] = frequency
        self.depth = self._payload["depth"] = depth

    def __repr__(self) -> str:
        return f"<Lavapy VibratoFilter (Payload={self._payload})>"


class Rotation(LavapyFilter):
    """
    Rotates the sound around the stereo channels/user headphones aka Audio Panning

    Here is an `Example <https://en.wikipedia.org/wiki/File:Fuse_Electronics_Tremolo_MK-III_Quick_Demo.ogv>`_ (without the reverb).

    Parameters
    ----------
    rotationHz: float
        The frequency of the audio rotating around the listener in hertz (0.2 is similar to the example above). This defaults to 0.0.
    """
    def __init__(self, rotationHz: float = 0.0) -> None:
        super().__init__(FilterName.Rotation)
        self.rotationHz = self._payload["rotationHz"] = rotationHz

    def __repr__(self) -> str:
        return f"<Lavapy RotationFilter (Payload={self._payload})>"


class Distortion(LavapyFilter):
    """
    Distorts the sound. This can generate some pretty unique audio effects.

    Attributes
    ----------
    sinOffset: float
        to do. This defaults to 0.0.
    sinScale: float
        to do. This defaults to 1.0.
    cosOffset: float
        to do. This defaults to 0.0.
    cosScale: float
        to do. This defaults to 1.0.
    tanOffset: float
        to do. This defaults to 0.0.
    tanScale: float
        to do. This defaults to 1.0.
    offset: float
        to do. This defaults to 0.0.
    scale: float
        to do. This defaults to 1.0.
    """
    def __init__(self, sinOffset: float = 0.0, sinScale: float = 1.0, cosOffset: float = 0.0, cosScale: float = 1.0, tanOffset: float = 0.0, tanScale: float = 1.0, offset: float = 0.0, scale: float = 1.0) -> None:
        super().__init__(FilterName.Distortion)
        self.sinOffset = self._payload["sinOffset"] = sinOffset
        self.sinScale = self._payload["sinScale"] = sinScale
        self.cosOffset = self._payload["cosOffset"] = cosOffset
        self.cosScale = self._payload["cosScale"] = cosScale
        self.tanOffset = self._payload["tanOffset"] = tanOffset
        self.tanScale = self._payload["tanScale"] = tanScale
        self.offset = self._payload["offset"] = offset
        self.scale = self._payload["scale"] = scale

    def __repr__(self) -> str:
        return f"<Lavapy DistortionFilter (Payload={self._payload})>"


class ChannelMix(LavapyFilter):
    """
    Mixes both channels (left and right) with a configurable factor on how much each channel affects the other. By default, both channel are kept separate from each other. Setting all factors to 0.5 means both channels get the same audio.

    Attributes
    ----------
    leftToLeft: float
        to do. This must be between 0 and 1. This defaults to 1.0.
    leftToRight: float
        to do. This must be between 0 and 1. This defaults to 0.0.
    rightToLeft: float
        to do. This must be between 0 and 1. This defaults to 0.0.
    rightToRight: float
        to do. This must be between 0 and 1. This defaults to 1.0.
    """
    def __init__(self, leftToLeft: float = 1.0, leftToRight: float = 0.0, rightToLeft: float = 0.0, rightToRight: float = 1.0) -> None:
        super().__init__(FilterName.ChannelMix)
        if leftToLeft < 0.0 or leftToLeft > 1.0:
            raise InvalidFilterArgument("LeftToLeft must be between 0 and 1.")
        if leftToRight < 0.0 or leftToRight > 1.0:
            raise InvalidFilterArgument("LeftToRight must be between 0 and 1.")
        if rightToLeft < 0.0 or rightToLeft > 1.0:
            raise InvalidFilterArgument("RightToLeft must be between 0 and 1.")
        if rightToRight < 0.0 or rightToRight > 1.0:
            raise InvalidFilterArgument("RightToRight must be between 0 and 1.")
        self.leftToLeft = self._payload["leftToLeft"] = leftToLeft
        self.leftToRight = self._payload["leftToRight"] = leftToRight
        self.rightToLeft = self._payload["rightToLeft"] = rightToLeft
        self.rightToRight = self._payload["rightToRight"] = rightToRight

    def __repr__(self) -> str:
        return f"<Lavapy ChannelMixFilter (Payload={self._payload})>"


class LowPass(LavapyFilter):
    """
    Suppresses higher frequencies, while allowing lower frequencies to pass through.

    Attributes
    ----------
    smoothing: float
        to do. This defaults to 20.0.
    """
    def __init__(self, smoothing: float = 20.0) -> None:
        super().__init__(FilterName.LowPass)
        self.smoothing = self._payload["smoothing"] = smoothing

    def __repr__(self) -> str:
        return f"<Lavapy LowPassFilter (Payload={self._payload})>"
