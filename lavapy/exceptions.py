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
__all__ = ("LavapyException",
           "NoNodesConnected",
           "NodeOccupied",
           "InvalidIdentifier",
           "WebsocketAlreadyExists",
           "LavalinkException",
           "LoadTrackError",
           "QueueEmpty",
           "BuildTrackError",
           "InvalidFilterArgument",
           "FilterAlreadyExists",
           "FilterNotApplied")


class LavapyException(Exception):
    """Base Lavapy exception. Every exception inherits from this."""


class LavalinkException(LavapyException):
    """Base exception raised when an error occurs communicating with Lavalink."""


class NoNodesConnected(LavapyException):
    """Exception raised when an operation is attempted with nodes and there are none connected."""


class NodeOccupied(LavapyException):
    """Exception raised when node identifiers conflict."""


class InvalidIdentifier(LavapyException):
    """Exception raised when an invalid ID is passed somewhere in Lavapy."""


class WebsocketAlreadyExists(LavapyException):
    """Exception raised when a new websocket connection is attempted but it already exists."""


class LoadTrackError(LavalinkException):
    """Exception raised when an error occurred when loading a track."""


class QueueEmpty(LavapyException):
    """Exception raised when attempting to get a track from an empty queue."""


class BuildTrackError(LavalinkException):
    """Exception raised when an error occurred when building a track."""


class InvalidFilterArgument(LavapyException):
    """Exception raised when an invalid argument is passed to a filter."""


class FilterAlreadyExists(LavapyException):
    """Exception raised when a new filter is attempted to be applied but it already exists."""


class FilterNotApplied(LavapyException):
    """Exception raised when a filter is attempted to be removed but it is not applied."""
