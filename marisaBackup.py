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
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
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

#Create bot instance
client = commands.Bot(command_prefix='>', intents = discord.Intents.all())

#Define global variables
display_queue = []
queue = []
voice_channel = None
count = 0
gctx = None

#Print a message to console to show bot is running and start loop for autoplay
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await channel_playing()


#Ping command
@client.command(name='ping', help=': This command is a latency ping owo')
async def ping(ctx):
    await ctx.send(f'**Pong Bitch** Latency: {round(client.latency * 1000)}ms')

#Hello command
@client.command(name='hello', help=': Use this to say hi to me!')
async def hello(ctx):
    await ctx.send(f'Hello Peasant!')

#Ominous function

#Gay command
@client.command(name='marigay', help=': i am now gay')
async def marigay(ctx):
    await ctx.send(file=discord.File('marisagay.jpg'))
    await ctx.send('Yeah Reimu is pretty hot')

#Gaming command
@client.command(name='gaming', help=': moment')
async def gaming(ctx):
    await ctx.send(f'moment')

@client.command(name='marisad', help=': sad mari peepo')
async def marisad(ctx):
    await ctx.send(file=discord.File('marisasad.png'))
    await ctx.send('cris in sans libre')

#VC Join command
@client.command(name='join', help=': Bring me to your current voice channel!')
async def join(ctx):
    if not await check_ifusr_inchannel(ctx):
        return
    else:
        channel = await check_ifusr_inchannel(ctx)

    await channel.connect()

#VC Leave command
@client.command(name='leave', help=': This tells me to leave the voice channel :(')
async def leave(ctx):
    global queue
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()
    voice_channel = ctx.message.guild.voice_client
    queue.clear()

#Play music command
@client.command(name='play', help=f': Use me to play music ;)')
async def play(ctx, url = ""):

    #Include global variables(idk if this is neccesary)
    global queue
    global voice_channel
    global count
    global gctx
    gctx = ctx

    #sets voice_channel to the voice channel the bot is connected to
    voice_channel = ctx.message.guild.voice_client

    #Remove empty elements from queue.
    #These occur due to the default arg of url
    print("enter if else queue")
    print(queue)
    fix_queue()

    #If bot is not connected to vc
    if voice_channel == None:
    #Check if user is in voice channel by running check func
        if not await check_ifusr_inchannel(ctx):
            return
        else:
            #Set channel equal to vc user is in
            channel = await check_ifusr_inchannel(ctx)
            queue.append(url)

        #Connect to voice channel user is in
        await channel.connect()

        #variable for channel the bot is connected to
        channel = ctx.message.guild.voice_client

        #Play song user requested
        await ctx.send(f'Please wait while I load your song!')
        player = await YTDLSource.from_url(queue[0], loop=client.loop)
        del(queue[0])

        channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)
        await ctx.send(f'Now playing: {player.title}')
    #If bot is connected to vc
    else:
        #If bot is already playing a song, add the song requested to queue
        if voice_channel.is_playing() or voice_channel.is_paused():
            queue.append(url)
            await ctx.send(f'`{url}` added to queue!')

        #Play next song in queue
        else:
            queue.append(url)
            await ctx.send(f'Please wait while I load your song!')
            player = await YTDLSource.from_url(queue[0], loop=client.loop)
            del(queue[0])

            voice_channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)
            await ctx.send(f'Now playing: {player.title}')

#Pause music command
@client.command(name='pause', help=f': Pauses the music, what did you think it did?')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.pause()

#Resume music command
@client.command(name='resume', help=f': Continues to play the music obviously.')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.resume()

#Remove from queue command
@client.command(name='rm', help=': This removes a song from the queue! Use: \">rm 2\"')
async def rm(ctx, number):
    global queue
    #global display_queue
    number = int(number)
    number = number - 1
    print(queue[number])

    try:
        del(queue[number])
        #del(display_queue[number])
        await ctx.send(f'This is now the current queue: `{queue}`')
    except:
        await ctx.send('The queue is either empty or the given number is out of range!')

#See queue command
@client.command(name='cq', help=': This shows the songs currently in queue')
async def cq(ctx):
    global queue
    await ctx.send('This is the current queue:\n')
    for val in queue:
        await ctx.send(f'`{val}`\n')

#Skip command
@client.command(name='skip', help=': This skips to the next song in queue!')
async def skip(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.stop()

    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=client.loop)
        del(queue[0])

        await ctx.send(f'Please wait while I load your song!')
        voice_channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)
        await ctx.send(f'Now playing: {player.title}')


async def fix_queue():
    global queue
    if (not queue):
        return
    else:
        while queue[0] == '':
            del(queue[0])

#Function to check if user is in a voice channel
async def check_ifusr_inchannel(ctx):
    if not ctx.message.author.voice:
        #If user not in voice channel, tell them so
        await ctx.send('At least join a voice channel first ばか')
        return False
    else:
        #Return vc that user is in
        return ctx.message.author.voice.channel

async def channel_playing():
    print("Check function started.\n")
    global voice_channel
    global gctx
    global queue
    while True:
        #Debug messages
        # print(voice_channel)
        # print(voice_channel == None)
        # print("\n")
        if not (voice_channel == None):
            #Debug messages
            # print(voice_channel.is_playing() == False)
            # print(voice_channel.is_paused() == False)
            # print(not (not queue))
            #NOT WORKING: print(not queue[0] == '')
            if voice_channel.is_playing() == False and voice_channel.is_paused() == False and (not (not queue)) and (not queue[0] == ''):
                print("Entered autoplay function\n")
                await play(gctx)
                await asyncio.sleep(5)
            else:
                print("Conditions for autoplay not met. Waiting 5 seconds.\n")#print("Conditions for autoplay not met. Conditions:\nVoice Channel playing: " + voice_channel.is_playing() + "\nVoice Channel paused: " + voice_channel.is_paused() + "\n ")
                await asyncio.sleep(5)
                pass
        else:
            print("Bot not connected to voice channel. Waiting 5 seconds.\n")#print("Conditions for autoplay not met. Conditions:\nVoice Channel playing: " + voice_channel.is_playing() + "\nVoice Channel paused: " + voice_channel.is_paused() + "\n ")
            await asyncio.sleep(5)
            pass

# async def display_queue(index):
#     print("Enter display queue func")
#     import pdb; pdb. set_trace()
#     index = int(index)
#     queue_player = await YTDLSource.from_url(queue[index], loop=client.loop)
#     return player.title

#Run bot
keep_alive.keep_alive()
asyncio.run(client.run(os.environ.get('MARISA_AUTH')))
