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


class PylinkException(Exception):
    """Base Pylink exception"""


class NoNodesConnected(PylinkException):
    """Exception raised when an operation is attempted with nodes and there none connected"""


class NodeOccupied(PylinkException):
    """Exception raised when node identifiers conflict"""


class InvalidIdentifier(PylinkException):
    """Exception raised when an invalid ID is passed somewhere in Pylink"""
