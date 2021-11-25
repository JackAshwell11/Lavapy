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

from base64 import b64encode
from typing import Dict, Optional

import aiohttp

from .exceptions import SpotifyAuthException

__all__ = ("SpotifyClient",)


class SpotifyClient:
    """
    Provides an interface for easily initialising and communicating with Spotify.

    Parameters
    ----------
    clientID: str
        The Spotify client ID of the application you want to connect to.
    clientSecret: str
        The Spotify client secret of the application you want to connect to.
    """
    def __init__(self, clientID: str, clientSecret: str) -> None:
        self._clientID: str = clientID
        self._clientSecret: str = clientSecret
        self._session: aiohttp.ClientSession = aiohttp.ClientSession()
        self._accessToken: Optional[str] = None

    def __repr__(self) -> str:
        return f"<Lavapy SpotifyClient)>"

    @property
    def clientID(self) -> str:
        """Returns the client ID of the Spotify client."""
        return self._clientID

    @property
    def clientSecret(self) -> str:
        """Returns the client secret of the Spotify client."""
        return self._clientSecret

    @property
    def session(self) -> aiohttp.ClientSession:
        """Returns the session used for communicating with Spotify."""
        return self._session

    @property
    def accessToken(self) -> Optional[str]:
        """Returns the access token used to authenticate with Spotify."""
        return self._accessToken

    @property
    def authHeaders(self) -> Dict[str, str]:
        """Returns the headers used for authenticating Spotify requests."""
        return {
            "Authorization": f"Bearer {self.accessToken}",
            "Content-Type": "application/json"
        }

    async def _getBearerToken(self) -> None:
        """|coro|

        Gets a Spotify bearer token for use when communicating with Spotify.
        """
        authTokenBytes = f"{self.clientID}:{self.clientSecret}".encode()
        bearerHeaders = {
            "Authorization": f"Basic {b64encode(authTokenBytes).decode()}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        async with self.session.post("https://accounts.spotify.com/api/token?grant_type=client_credentials", headers=bearerHeaders) as response:
            if response.status != 200:
                raise SpotifyAuthException("An error occurred while authenticating with Spotify.")
            data = await response.json()
        self._accessToken = data["access_token"]
