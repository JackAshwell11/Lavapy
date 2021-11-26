Quickstart
==========

To use Lavapy, you need to have Lavalink 3.3 or higher (preferably 3.4 since you won't be able to access some features without it). For details on how to install and start it, see :ref:`setupLavalink`.

Basic Bot Example
-----------------

Lavapy is designed to work with discord.py 1.7.3 and up. Previous versions may work, however, problems will not be fixed due to those versions being deprecated.

Here is an example for a starting bot which will play a Youtube track using a search query in a discord voice channel:

.. code:: py

    from discord.ext import commands
    import lavapy

    bot = commands.Bot(command_prefix="!")


    async def initialiseNodes():
        """
        Wait until the bot is ready then create a Lavapy node
        """
        await bot.wait_until_ready()

        await lavapy.NodePool.createNode(client=bot,
                                         host="0.0.0.0",
                                         port=2333,
                                         password="LAVALINK_PASSWORD")


    @bot.command()
    async def play(ctx: commands.Context, *query) -> None:
        """
        Play a Youtube song from a given search query.

        If the bot is not connected, connect it to the user's voice channel. For this
        to work, the user must be connected to a voice channel
        """
        if not ctx.voice_client:
            # Bot is not connected to a voice channel
            try:
                player: lavapy.Player = await ctx.author.voice.channel.connect(cls=lavapy.Player)
            except AttributeError:
                # User is not connected to a voice channel
                await ctx.channel.send("You must be connected to a voice channel")
                return
        else:
            # Bot is connected to a voice channel
            player: lavapy.Player = ctx.voice_client

        # Get tracks based on the given search query
        track = await lavapy.YoutubeTrack.search(" ".join(query), player.node)
        await player.play(track)


    bot.loop.create_task(initialiseNodes())
    bot.run("BOT_TOKEN")

Spotify Bot Example
-------------------

Lavapy also supports querying for Spotify tracks, playlists, and albums. Here is a basic example which will play a Spotify track using a Spotify link in a discord voice channel:

.. code:: py

    from discord.ext import commands
    import lavapy
    from lavapy.ext import spotify

    bot = commands.Bot(command_prefix="!")


    async def initialiseNodes():
        """
        Wait until the bot is ready then create a Lavapy node
        """
        await bot.wait_until_ready()

        await lavapy.NodePool.createNode(client=bot,
                                         host="0.0.0.0",
                                         port=2333,
                                         password="LAVALINK_PASSWORD",
                                         spotifyClient=spotify.SpotifyClient("client ID", "client secret"))


    @bot.command()
    async def play(ctx: commands.Context, query) -> None:
        """
        Play a Spotify song from a given URL.

        If the bot is not connected, connect it to the user's voice channel. For this
        to work, the user must be connected to a voice channel
        """
        if not ctx.voice_client:
            # Bot is not connected to a voice channel
            try:
                player: lavapy.Player = await ctx.author.voice.channel.connect(cls=lavapy.Player)
            except AttributeError:
                # User is not connected to a voice channel
                await ctx.channel.send("You must be connected to a voice channel")
                return
        else:
            # Bot is connected to a voice channel
            player: lavapy.Player = ctx.voice_client

        # Get tracks based on the given URL
        track = await spotify.SpotifyTrack.search(query, player.node)
        await player.play(track)


    bot.loop.create_task(initialiseNodes())
    bot.run("BOT_TOKEN")