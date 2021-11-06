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
    :show-inheritance:

Queue
-----

.. autoclass:: Queue
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

Filters
---------

.. autoclass:: LavapyFilter
    :members:
.. autoclass:: Equalizer
    :members:
    :show-inheritance:
.. autoclass:: Karaoke
    :members:
    :show-inheritance:
.. autoclass:: Timescale
    :members:
    :show-inheritance:
.. autoclass:: Tremolo
    :members:
    :show-inheritance:
.. autoclass:: Vibrato
    :members:
    :show-inheritance:
.. autoclass:: Rotation
    :members:
    :show-inheritance:
.. autoclass:: Distortion
    :members:
    :show-inheritance:
.. autoclass:: ChannelMix
    :members:
    :show-inheritance:
.. autoclass:: LowPass
    :members:
    :show-inheritance:

Enums
-----

.. autoclass:: FilterName
    :members:
    :show-inheritance:

Events
------

.. autoclass:: LavapyEvent
    :members:
.. autoclass:: TrackStartEvent
    :members:
    :show-inheritance:
.. autoclass:: TrackEndEvent
    :members:
    :show-inheritance:
.. autoclass:: TrackExceptionEvent
    :members:
    :show-inheritance:
.. autoclass:: TrackStuckEvent
    :members:
    :show-inheritance:
.. autoclass:: WebsocketClosedEvent
    :members:
    :show-inheritance:

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
.. autoexception:: BuildTrackError
    :show-inheritance:
.. autoexception:: FilterAlreadyExists
    :show-inheritance:
.. autoexception:: FilterNotApplied
    :show-inheritance: