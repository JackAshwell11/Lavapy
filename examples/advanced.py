# Builtin
from typing import Dict, Optional
from datetime import datetime
# Pip
from discord import VoiceRegion, VoiceChannel, Embed, Colour
from discord.ext import commands
# Custom
import lavapy
from lavapy.ext import spotify

# Create discord bot
bot = commands.Bot(command_prefix="$")


class CustomPlayer(lavapy.Player):
    """Custom lavapy Player class to add additional functionality."""
    def __init__(self, bot: commands.Bot, channel: VoiceChannel) -> None:
        super().__init__(bot, channel)
        self.context: Optional[commands.Context] = None

    async def playNext(self) -> None:
        # Test if the queue is empty
        if self.queue.isEmpty:
            # All tracks done so disconnect and cleanup
            await self.context.send("Finished playing all tracks. Disconnecting")
            await self.destroy()
        else:
            # Play the next track
            await self.play(self.queue.next())


class Music(commands.Cog):
    """Music cog to manage music related commands and operations."""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.bot.loop.create_task(self.initialiseNodes())

    @staticmethod
    async def initialiseNodes() -> None:
        """Wait until the bot is ready then create a Lavapy node."""
        # Wait until the bot is ready
        await bot.wait_until_ready()

        # Create the lavapy node
        await lavapy.NodePool.createNode(client=bot,
                                         host="192.168.1.227",
                                         port=2333,
                                         password="",
                                         region=VoiceRegion.london,
                                         spotifyClient=spotify.SpotifyClient(clientID="client ID",
                                                                             clientSecret="client secret"),
                                         identifier="Main Node")
        print("Node ready")

    @commands.Cog.listener()
    async def on_lavapy_track_start(self, player: CustomPlayer, track: lavapy.Track) -> None:
        await player.context.send(embed=Embed(title="Now Playing:", description=f"{track.title}\n\nLink: {track.uri}", colour=Colour.red(), timestamp=datetime.now()))

    @commands.Cog.listener()
    async def on_lavapy_track_end(self, player: CustomPlayer, track: lavapy.Track, reason: str) -> None:
        await player.playNext()

    @commands.Cog.listener()
    async def on_lavapy_track_exception(self, player: CustomPlayer, track: lavapy.Track, exception: Dict[str, str]) -> None:
        await player.playNext()

    @commands.Cog.listener()
    async def on_lavapy_track_stuck(self, player: CustomPlayer, track: lavapy.Track, threshold: float) -> None:
        await player.playNext()

    @commands.command(aliases=["j"])
    async def join(self, ctx: commands.Context, channel: VoiceChannel = None) -> None:
        if not channel:
            # Check if the user is connected to voice
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                await ctx.send("You must be in a voice channel in order to use this command.")
                return
        # Connect to a voice channel with lavapy.Player
        # noinspection PyTypeChecker
        player: CustomPlayer = await channel.connect(cls=CustomPlayer)
        player.context = ctx
        await ctx.send(f"Joined the voice channel {channel.mention}")

    @commands.command(aliases=["dc", "disconnect"])
    async def leave(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            await ctx.send("You must be in a voice channel in order to use this command.")
            return
        # Get the player which is currently playing
        player: CustomPlayer = ctx.voice_client
        await player.destroy()
        await ctx.send("Player has left the channel.")

    @commands.command(aliases=["p"])
    async def play(self, ctx: commands.Context, *query) -> None:
        # Check if the player is in a channel
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        player: CustomPlayer = ctx.voice_client
        if not player:
            # invoke of $join failed since the user wasn't connected
            return
        # Make sure its just a string since search queries will be tuples
        query = " ".join(query)
        # Find out what track type it is and then search
        if "spotify.com" in query:
            query, type = spotify.decodeSpotifyQuery(query)
        else:
            query, type = lavapy.decodeQuery(query)
        result = await type.search(query, partial=True)
        # Make sure result is not none
        if result is None:
            await ctx.send("No results were found for that search")
            return
        # If the player is already playing, push result to the queue
        if player.isPlaying:
            if isinstance(result, lavapy.MultiTrack):
                player.queue.addIterable(result.tracks)
            else:
                player.queue.add(result)
            return
        # Play the track(s)
        await player.play(result)

    @commands.command()
    async def pause(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            await ctx.send("Bot is not connected to voice")
        player: CustomPlayer = ctx.voice_client
        # Make sure the player isn't paused
        if player.isPaused:
            await ctx.send("Player is already paused")
        await player.pause()
        await ctx.send("Player has been paused")

    @commands.command()
    async def resume(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            await ctx.send("Bot is not connected to voice")
        player: CustomPlayer = ctx.voice_client
        # Make sure the player isn't playing
        if not player.isPaused:
            await ctx.send("Player is already playing")
        await player.resume()
        await ctx.send("Player has been resumed")

    @commands.command()
    async def stop(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            await ctx.send("Bot is not connected to voice")
        player: CustomPlayer = ctx.voice_client
        # Make sure the player isn't already stopped
        if not player.isPaused:
            await ctx.send("Player is already stopped")
        await player.stop()
        await ctx.send("Player has been stopped")

    @commands.command()
    async def next(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            await ctx.send("Bot is not connected to voice")
        player: CustomPlayer = ctx.voice_client
        # Get the next item in the queue
        try:
            track = player.queue.next()
        except lavapy.QueueEmpty:
            await ctx.send("Queue is empty.")
            return
        await player.play(track)

    @commands.command()
    async def previous(self, ctx: commands.Context) -> None:
        if not ctx.voice_client:
            await ctx.send("Bot is not connected to voice")
        player: CustomPlayer = ctx.voice_client
        # Get the previous item in the queue
        try:
            track = player.queue.previous()
        except lavapy.QueueEmpty:
            await ctx.send("Queue is empty.")
            return
        await player.play(track)



# Add the music cog
bot.add_cog(Music(bot))
# Start the bot
bot.run("token")
