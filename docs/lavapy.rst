.. currentmodule:: lavapy

API Reference
=============

NodePool
--------

.. autoclass:: NodePool
    :members:

Node
----

.. autoclass:: Node
    :members:
.. autoclass:: Stats
    :members:

Player
------

.. autoclass:: Player
    :members:
.. autoclass:: Queue
    :members:

Playables
---------

.. autoclass:: Searchable
    :members:
.. autoclass:: Identifiable
    :members:
.. autoclass:: Track
    :members:
.. autoclass:: MultiTrack
    :members:
.. autoclass:: PartialResource
    :members:
.. autoclass:: YoutubeTrack
    :members:
    :show-inheritance:
.. autoclass:: YoutubeMusicTrack
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
.. autoexception:: LavalinkException
    :show-inheritance:
.. autoexception:: NoNodesConnected
    :show-inheritance:
.. autoexception:: NodeOccupied
    :show-inheritance:
.. autoexception:: InvalidIdentifier
    :show-inheritance:
.. autoexception:: WebsocketAlreadyExists
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
