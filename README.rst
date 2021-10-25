Lavapy
========

.. image:: https://img.shields.io/pypi/v/Lavapy
    :target: https://pypi.org/project/Lavapy/
    :align: center

.. image:: https://img.shields.io/pypi/pyversions/Lavapy
    :target: https://pypi.org/project/Lavapy/
    :align: center

.. image:: https://img.shields.io/github/license/Aspect1103/Lavapy
    :target: LICENSE
    :align: center

A powerful and robust python library for interacting with Lavalink.

Installation
---------------------------
Lavapy requires Python 3.8 or higher

.. code:: sh

    # Windows
    py -3.8 -m pip install -U lavapy

    # Linux/macOS
    python3.8 -m pip install -U lavapy

Features
---------------------------
TO DO

Usage
---------------------------
A simple and easy example to connect to a voice channel and play a Youtube song based on a given search query.

.. code:: py

    from discord.ext import commands
    import lavapy

    bot = commands.Bot(command_prefix="$")


    async def initialiseNodes():
        """
        Wait until the bot is ready then create a Lavapy node
        """
        await bot.wait_until_ready()

        await lavapy.createNode(bot, "0.0.0.0", 2333, "LAVALINK_PASSWORD")


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
        tracks = await player.getYoutubeTracks(" ".join(query))
        await player.play(tracks[0])


    bot.loop.create_task(initialiseNodes())
    bot.run("BOT_TOKEN")

Links
---------------------------
- `Official Documentation <https://lavapy.readthedocs.io/en/latest/>`_
- `Source Code <https://github.com/Aspect1103/Lavapy>`_
- `Issue Tracker <https://github.com/Aspect1103/Lavapy/issues>`_
