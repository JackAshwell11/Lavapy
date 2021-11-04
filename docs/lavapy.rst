.. currentmodule:: lavapy

API Reference
=============

Abstract Base Classes
---------------------

.. autoclass:: Playable
    :members:

NodePool
--------

.. autoclass:: NodePool
    :members:

Node
----

.. autoclass:: Node
    :members:

Player
------

.. autoclass:: Player
    :members:

Tracks
------

.. autoclass:: Track
    :members:
    :show-inheritance:

.. autoclass:: SoundcloudTrack
    :members:
    :show-inheritance:

.. autoclass:: YoutubeTrack
    :members:
    :show-inheritance:

.. autoclass:: YoutubeMusicTrack
    :members:
    :show-inheritance:

Playlists
---------

.. autoclass:: Playlist
    :members:
    :show-inheritance:

.. autoclass:: YoutubePlaylist
    :members:
    :show-inheritance:

Equalizer
---------

.. autoclass:: Equalizer
    :members:

Queue
-----

.. autoclass:: Queue
    :members:

Exceptions
----------

.. autoexception:: LavapyException
.. autoexception:: NoNodesConnected
    :show-inheritance:
.. autoexception:: NodeOccupied
    :show-inheritance:
.. autoexception:: InvalidIdentifier
    :show-inheritance:
.. autoexception:: WebsocketAlreadyExists
    :show-inheritance:
.. autoexception:: LavalinkException
    :show-inheritance:
.. autoexception:: LoadTrackError
    :show-inheritance:
.. autoexception:: QueueEmpty
    :show-inheritance:


