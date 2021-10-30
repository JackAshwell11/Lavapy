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

from typing import Dict, Any, List

__all__ = ("Track",
           "Playlist",)


class Track:
    """
    A Lavapy Track object. This should not be created manually, instead use the player object to get tracks

    Parameters
    ----------
    id: str
        The unique base64 track ID which can be used to rebuild a track
    info: Dict[str, Any]
        The raw track info

    Attributes
    ----------
    id: str
        The unique base64 track ID which can be used to rebuild a track
    info: Dict[str, Any]
        The raw track info
    identifier: str
        The track's unique identifier
    isSeekable: bool
        A bool stating if a track can be seeked or not
    author: str
        The author of the track
    length: int
        The duration of the track in seconds
    type: str
        The source site of the track
    title: str
        The title of the track
    uri: str
        The track's URI
    """
    def __init__(self, id: str, info: Dict[str, Any]) -> None:
        self.id: str = id
        self.info: Dict[str, Any] = info
        self.identifier: str = info.get("identifier")
        self.isSeekable: bool = info.get("isSeekable")
        self.author: str = info.get("author")
        self.length: int = info.get("length")
        self.type: str = info.get("sourceName")
        self.title: str = info.get("title")
        self.uri: str = info.get("uri")

    def __repr__(self) -> str:
        return f"<Lavapy Track (Identifier={self.identifier}) (Type={self.type})>"


class Playlist:
    """
    A Lavapy Playlist object. This should not be created manually, instead use the player object to get playlists

    Parameters
    ----------
    name: str
        The playlist's name
    trackArr: List[Dict[str, Any]]
        A list of Lavapy Track objects

    Attributes
    ----------
    name: str
        The playlist's name
    tracks: List[Track]
        A list of Lavapy Track objects
    """
    def __init__(self, name: str, trackArr: List[Dict[str, Any]]):
        self.name: str = name
        self.tracks: List[Track] = [Track(track["track"], track["info"]) for track in trackArr]

    def __repr__(self):
        return f"<Lavapy Playlist (Name={self.name}) (Track count={len(self.tracks)})>"
