Frequently Asked Questions
==========================

Frequently asked questions about Lavalink and Lavapy.

Lavalink
--------

What Java version is needed to run Lavalink.jar?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Java version 11+. The latest version of Java is preferable in most cases.

.. _setupLavalink:

How do I run Lavalink.jar?
~~~~~~~~~~~~~~~~~~~~~~~~~~

Firstly, you need to download and install Java 11+ (preferably the latest version) for your desired OS.

- Create a directory for storing Lavalink.jar and application.yml.
- Download the latest `Lavalink.jar` from the `CI Server <https://ci.fredboat.com/viewLog.html?buildId=lastSuccessful&buildTypeId=Lavalink_Build&tab=artifacts&guest=1>`_.
- Create an application.yml. Here is an `Example <https://github.com/freyacodes/Lavalink/blob/master/LavalinkServer/application.yml.example>`_.
- In your terminal, run `cd LavalinkDirectory && java -jar Lavalink.jar`.

Your server should now be running and ready to be connected to.

Why is it saying "Cannot connect to host?"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to have a Lavalink node setup before you cna use this library, see :ref:`setupLavalink`.

General
-------

What experience do I need?
~~~~~~~~~~~~~~~~~~~~~~~~~~

This library requires that you have some experience with Python, asynchronous programming, and the discord.py library.

Why is it saying "No module named Lavapy found?"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to :doc:`install <installing>` the package before you can use it.

Lavapy
------

How do I connect to my Lavalink server?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connecting to a Lavalink node is simple in Lavapy. For example:

.. code:: py

    import lavapy


    node = await lavapy.NodePool.createNode(client=bot,
                                            host="0.0.0.0",
                                            port=2333,
                                            password="LAVALINK_PASSWORD")

Run the above code from an asynchronous environment, usually created as a task before your bot is ran or in your cogs __init__ function. Remember to replace the fields appropriate to what you have set in your `application.yml`.

How do I get retrieve my created nodes?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lavapy has multiple algorithms which allow for easy retrieval of your nodes. These include:

The minPlayers algorithm which selects the best node based on the amount of players it has:

.. code:: py

    node = lavapy.NodePool.minPlayers()

The balanced algorithm which selects the best node based on it's penalty as determined by :class:`lavapy.Stats`:

.. code:: py

    node = lavapy.NodePool.balanced()

The identifier algorithm which selects a specific node based on a given identifier:

.. code:: py

    node = lavapy.NodePool.identifier("node1")

The closestNode algorithm which selects the best node based on a given region:

.. code:: py

    node = lavapy.NodePool.closestNode(VoiceRegion.london)

The extension algorithm which selects a specific node which includes a client used for a given extension:

.. code:: py

    from lavapy.ext import spotify

    node = lavapy.NodePool.extension(spotify.SpotifyTrack)

How do I listen to events?
~~~~~~~~~~~~~~~~~~~~~~~~~~

Lavapy makes use of the built in event dispatcher in discord.py. This means that you can listen to Lavapy events the same way you listen to discord.py events.

Outside a cog:

.. code:: py

    @bot.event
    async def on_lavapy_websocket_open(node: Node):
        print(f"Node {node.identifier} is ready!")

Inside a cog:

.. code:: py

    @commands.Cog.listener()
    async def on_lavapy_websocket_open(node: Node):
        print(f"Node {node.identifier} is ready!")

How do I connect to a voice channel?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Joining a voice channel is easy in Lavapy, just pass the player object to the cls `kwarg` in VoiceChannel.connect()

.. code:: py

    channel: discord.VoiceChannel = bot.get_channel(822868109709803580)
    player: lavapy.Player = lavapy.Player = await channel.connect(cls=lavapy.Player)

Searching Tracks
----------------

How do I search Youtube for a track?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lavapy supports both queries and URL links to allow much more flexibility when searching for tracks. After connecting to a node, simply:

.. code:: py

    track = await lavapy.YoutubeTrack.search("Rick Astley - Never Gonna Give You Up")

Or:

.. code:: py

    track = await lavapy.YoutubeTrack.search("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

How can I get more than one result?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lavapy will return a list of possible results for a track if the given query is a search query. A list cannot be returned if the query is a URL. Here is an example:

.. code:: py

    track = await lavapy.YoutubeTrack.search("Rick Astley - Never Gonna Give You Up", returnFirst=False)

Can I search Soundcloud too?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, Lavapy supports Soundcloud tracks as well. Here is an example:

.. code:: py

    track = await lavapy.SoundcloudTrack.search("Rick Astley - Never Gonna Give You Up")

How about Discord mp3 files?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes, Lavapy supports mp3 files uploaded to Discord as well. Here is an example:

.. code:: py

    track = await lavapy.LocalTrack.search("https://cdn.discordapp.com/attachments/881224361015672863/888010232016564254/m_SURF_-_Take_Care.mp3")

What is a PartialResource and how do I use it?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of searching for and retrieving a track immediately, a PartialResource allows you to queue a song and search at playtime. This allows large amounts of track data to be stored, and processed without querying the REST API continuously. Here is an example with a Youtube track:

.. code:: py

    track = await lavapy.YoutubeTrack.search("Rick Astley - Never Gonna Give You Up", partial=True)
    await player.play(track)
    await ctx.send(f"**Now playing:** {track.title}.")

Filters
-------

.. node::

    Only Lavalink 3.4 and above supports filters.

How can I add a filter?
~~~~~~~~~~~~~~~~~~~~~~~

Lavapy supports adding multiple filters to a player to change how the track is player. Here is a list of current filters:

- :class:`lavapy.Equalizer`.
- :class:`lavapy.Karaoke`.
- :class:`lavapy.Timescale`.
- :class:`lavapy.Tremolo`.
- :class:`lavapy.Vibrato`.
- :class:`lavapy.Rotation`.
- :class:`lavapy.Distortion`.
- :class:`lavapy.ChannelMix`.
- :class:`lavapy.LowPass`.

Here is an example of how you can add a filter to a player:

.. code:: py

    await player1.addFilter(lavapy.Karaoke())

How can I remove a filter?
~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to how you add filters with Lavapy, removing filters is easy too. The filter argument can be either a type or the instantiated filter. Here is an example:

.. code:: py

    await player1.removeFilter(lavapy.Karaoke)

How can I get currently applied filters?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Getting currently applied filters for a player is easy. Here is an example:

.. code:: py

    filters = player.filters()

This is returned as dictionary with the key being the filter name and the value being the actual filter.

Common operations
-----------------

What other operations can I do with lavapy?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here are some other operations that can be done with Lavapy which haven't been discussed above:

.. code:: py

    # Pause the current song
    await player.pause()

    # Resume the current song
    await player.resume()

    # Stop the current song from playing
    await player.stop()

    # Stop the current song from playing, disconnect and cleanup the player
    await player.disconnect()

    # Move the player to another channel
    await player.moveTo(channel)

    # Set the player volume
    await player.setVolume(30)

    # Seek the currently playing song (position is an integer of seconds)
    await player.seek(position)

    # Check if the player is playing
    player.isPlaying

    # Check if the player is connected
    player.isConnected

    # Check if the player is paused
    player.isPaused

    # Check if the player is dead (a player is considered dead if it has been destroyed and removed from stored players)
    player.isDead

    # Build a track from the unique track base64 identifier
    await node.build_track(lavapy.YouTubeTrack, "UniqueBase64TrackIdentifier")

    # Disconnect and cleanup a node
    await node.disconnect()

    # Common node properties
    node.client
    node.host
    node.port
    node.password
    node.region
    node.secure
    node.heartbeat
    node.spotifyClient
    node.identifier
    node.players
    node.stats
    node.penalty

    # Common player properties
    player.guild
    player.node
    player.track
    player.volume
    player.queue
    player.position

Spotify
-------

This is a QoL extension which helps in searching for and querying tracks from Spotify URLs or search queries.

How do I connect to Spotify?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get started, create a `SpotifyClient` and pass in your credentials. This can then be passed to your Node(s). Here is an example:

.. code:: py

    import lavapy
    from lavapy.ext import spotify


    node = await lavapy.NodePool.createNode(client=bot,
                                            host="0.0.0.0",
                                            port=2333,
                                            password="LAVALINK_PASSWORD"
                                            spotifyClient=spotify.SpotifyClient(clientID="client ID", clientSecret="client secret"))

How do I search for Spotify resources?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Searching for Spotify resources is very similar to the core library. All the same functionality in the core library is available in the Spotify extension. Here is an example with a track:

.. code:: py

    from lavapy.ext import spotify

    track = await spotify.SpotifyTrack.search("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT")

And a playlist:

.. code:: py

    from lavapy.ext import spotify

    track = await spotify.SpotifyPlaylist.search("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")

And finally an album:

.. code:: py

    from lavapy.ext import spotify

    track = await spotify.SpotifyAlbum.search("https://open.spotify.com/album/2QT5OxkgbFNpZXVJDEmssK")