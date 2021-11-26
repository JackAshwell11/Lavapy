.. currentmodule:: lavapy

API Reference
=============

NodePool
--------

.. autoclass:: NodePool
    :members:

Node
----

Node
~~~~

.. autoclass:: Node
    :members:

Stats
~~~~~

.. autoclass:: Stats
    :members:

Player
------

Player
~~~~~~

.. autoclass:: Player
    :members:

Queue
~~~~~

.. autoclass:: Queue
    :members:

Playables
---------

.. note::
    Remember to check if the specific source is enabled in your Lavalink application.yml.

Playable
~~~~~~~~

.. autoclass:: Playable
    :members:

PartialResource
~~~~~~~~~~~~~~~

.. autoclass:: PartialResource
    :members:

Track
~~~~~

.. autoclass:: Track
    :members:

MultiTrack
~~~~~~~~~~

.. autoclass:: MultiTrack
    :members:

YoutubeTrack
~~~~~~~~~~~~

.. autoclass:: YoutubeTrack
    :members:
    :show-inheritance:

YoutubeMusicTrack
~~~~~~~~~~~~~~~~~

.. autoclass:: YoutubeMusicTrack
    :members:
    :show-inheritance:

SoundcloudTrack
~~~~~~~~~~~~~~~~~

.. autoclass:: SoundcloudTrack
    :members:
    :show-inheritance:


LocalTrack
~~~~~~~~~~

.. autoclass:: LocalTrack
    :members:
    :show-inheritance:

YoutubePlaylist
~~~~~~~~~~~~~~~

.. autoclass:: YoutubePlaylist
    :members:
    :show-inheritance:

Filters
---------

LavapyFilter
~~~~~~~~~~~~

.. autoclass:: LavapyFilter
    :members:

Equalizer
~~~~~~~~~

.. autoclass:: Equalizer
    :members:
    :show-inheritance:

Karaoke
~~~~~~~

.. autoclass:: Karaoke
    :members:
    :show-inheritance:

Timescale
~~~~~~~~~

.. autoclass:: Timescale
    :members:
    :show-inheritance:

Tremolo
~~~~~~~

.. autoclass:: Tremolo
    :members:
    :show-inheritance:

Vibrato
~~~~~~~

.. autoclass:: Vibrato
    :members:
    :show-inheritance:

Rotation
~~~~~~~~

.. autoclass:: Rotation
    :members:
    :show-inheritance:

Distortion
~~~~~~~~~~

.. autoclass:: Distortion
    :members:
    :show-inheritance:

ChannelMix
~~~~~~~~~~

.. autoclass:: ChannelMix
    :members:
    :show-inheritance:

LowPass
~~~~~~~

.. autoclass:: LowPass
    :members:
    :show-inheritance:

Events
------

LavapyEvent
~~~~~~~~~~~

.. autoclass:: LavapyEvent
    :members:

TrackStartEvent
~~~~~~~~~~~~~~~

.. autoclass:: TrackStartEvent
    :members:
    :show-inheritance:

TrackEndEvent
~~~~~~~~~~~~~

.. autoclass:: TrackEndEvent
    :members:
    :show-inheritance:

TrackExceptionEvent
~~~~~~~~~~~~~~~~~~~

.. autoclass:: TrackExceptionEvent
    :members:
    :show-inheritance:

TrackStuckEvent
~~~~~~~~~~~~~~~

.. autoclass:: TrackStuckEvent
    :members:
    :show-inheritance:

WebsocketOpenEvent
~~~~~~~~~~~~~~~~~~

.. autoclass:: WebsocketOpenEvent
    :members:
    :show-inheritance:

WebsocketClosedEvent
~~~~~~~~~~~~~~~~~~~~

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
.. autoexception:: InvalidSeekPosition
    :show-inheritance:
.. autoexception:: WebsocketAlreadyExists
    :show-inheritance:
.. autoexception:: QueueEmpty
    :show-inheritance:
.. autoexception:: InvalidFilterArgument
    :show-inheritance:
.. autoexception:: FilterAlreadyExists
    :show-inheritance:
.. autoexception:: FilterNotApplied
    :show-inheritance:
.. autoexception:: InvalidNodeSearch
    :show-inheritance:
.. autoexception:: LavalinkException
    :show-inheritance:
.. autoexception:: LoadTrackError
    :show-inheritance:
.. autoexception:: BuildTrackError
    :show-inheritance:
