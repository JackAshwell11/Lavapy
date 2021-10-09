"""
Copyright (C) 2021 Aspect1103

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from typing import Dict, Any


class Track:
    def __init__(self, id: str, info: Dict[str, Any]) -> None:
        self.id = id
        self.info = info
        self.identifier = info.get("identifer")
        self.isSeekable = info.get("isSeekable")
        self.author = info.get("author")
        self.length = info.get("length")
        self.type = info.get("sourceName")
        self.title = info.get("title")
        self.uri = info.get("uri")

    def __repr__(self) -> str:
        return f"Pylink Track (Identifier={self.identifier}) (Type={self.type})"
