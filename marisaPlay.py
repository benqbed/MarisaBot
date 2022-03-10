import discord
from discord.ext import commands
import os
import keep_alive
import youtube_dl
import asyncio
import time

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


# Create bot instance
client = commands.Bot(command_prefix='>', intents=discord.Intents.all())
queue = []
count = 0
song_starttime = 0


# Print a message to console to show bot is running
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


# Ping command
@client.command(name='ping', help=': This command is a latency ping owo')
async def ping(ctx):
    await ctx.send(f'**Pong Bitch** Latency: {round(client.latency * 1000)}ms')

@client.command(name='join', help=': Bring me to your current voice channel!')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send('At least join a voice channel first ばか')
        return
    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()


# VC Leave command
@client.command(name='leave', help=': This tells me to leave the voice channel :(')
async def leave(ctx):
    global count
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()
    count = 0


# Play music command
@client.command(name='play', help=f': Use me to play music ;)')
async def play(ctx, url = ""):

    #variable to keep track of song queue
    global queue
    #variable to check if a song has been added to queue
    global count
    #variable for keeping track of song start time
    global song_starttime

    #Tbh idk what this really does
    server = ctx.message.guild
    #sets voice_chanel to the voice channel the bot is
    #connected to, if connected to one
    voice_channel = server.voice_client

    #Check if user is in voice channel
    if voice_channel == None:
        if not await check_ifusr_inchannel(ctx, url):
            return
        else:
            channel = await check_ifusr_inchannel(ctx, url)

        #Connect to voice channel user is in
        await channel.connect()

        #variable for channel the bot is connected to
        channel = server.voice_client

        #Play song user requested
        #else:
        #async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=client.loop)
            #test code for moment
            #with ytdl as ydl:
            #    dictMeta = ydl.extract_info(queue[0])
            #await ctx.send('Song length is ' + str(dictMeta['duration']) + ' seconds')

        channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)
        song_starttime = int(time.time())
        del(queue[0])
        await ctx.send(f'Now playing: {player.title}')

            #time.sleep(dictMeta['duration'] + 2)
            #player = await YTDLSource.from_url(queue[0], loop=client.loop)
            #channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)

    else:
        #In here needs to be the autoplay function
        if voice_channel.is_playing() or voice_channel.is_paused():
            queue.append(url)
            await ctx.send(f'`{url}` added to queue!')

            command_runtime = int(time.time())
            time_left = command_runtime - song_starttime
            await asyncio.sleep(time_left)

            player = await YTDLSource.from_url(queue[0], loop=client.loop)
            with ytdl as ydl:
                dictMeta = ydl.extract_info(queue[0])

            voice_channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)
            song_starttime = int(time.time())
            del(queue[0])
            await ctx.send(f'Now playing: {player.title}')



            #with ytdl as ydl:
            #    dictMeta = ydl.extract_info(queue[0])
            #await ctx.send('Song length is ' + str(dictMeta['duration']) + 'seconds')

        else:
            #async with ctx.typing():
            queue.append(url)
            player = await YTDLSource.from_url(queue[0], loop=client.loop)
            with ytdl as ydl:
                dictMeta = ydl.extract_info(queue[0])
                #await ctx.send('Song length is ' + str(dictMeta['duration']) + ' seconds')

            flag = True
            while flag == True:
                try:
                    voice_channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)
                    flag = False
                except:
                    await asyncio.sleep(1)
                    return
            song_starttime = int(time.time())
            del(queue[0])
            await ctx.send(f'Now playing: {player.title}')

async def check_ifusr_inchannel(ctx, url):
    global count
    global queue
    if not ctx.message.author.voice:
        await ctx.send('At least join a voice channel first ばか')
        return False
    else:
        # add the first song the user provides to queue
        if count == 0:
            queue.append(url)
            count += 1
        # Determine channel to connect to
        return ctx.message.author.voice.channel

# async def channel_playing():
#     while True:
#         if not voice_channel.is_playing():
#             player = await YTDLSource.from_url(queue[0], loop=client.loop)
#         else:
#             await asyncio.sleep(5)
#             return

keep_alive.keep_alive()
asyncio.run(client.run(os.environ['MARISA_AUTH']))
