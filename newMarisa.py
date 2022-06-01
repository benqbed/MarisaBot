from pytube import YouTube
from pytube import Search
from nextcord.ext import commands
import nextcord
import asyncio

queue = []

ffmpeg_options = {
    'options': '-vn'
}

client = commands.Bot(command_prefix='>', intents = nextcord.Intents.all())

#Function to check if user is in a voice channel
async def check_ifusr_inchannel(ctx):
    if not ctx.message.author.voice:
        #If user not in voice channel, tell them so
        await ctx.send('At least join a voice channel first ばか')
        return False
    else:
        #Return vc that user is in
        return ctx.message.author.voice.channel

#Function to get a song requested by user
async def getSong(url):
    ytSearch = Search(url)
    ytSearch = ytSearch.results[0]
    filename = ytSearch.streams.desc().first().download('Files/')
    return nextcord.FFmpegPCMAudio(source = filename, **ffmpeg_options)

#Print a message to console to show bot is running and start loop for autoplay
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

#VC Join command
@client.command(name='join', help=': Bring me to your current voice channel!')
async def join(ctx):
    voice_channel = await check_ifusr_inchannel(ctx)
    if not voice_channel:
        return 0
    if not ctx.message.guild.voice_client:
        await voice_channel.connect()
        voice_channel = ctx.message.guild.voice_client
        return voice_channel
    else:
        await ctx.send('I\'m already in a voice channel ばか')
        return 0

@client.command(name='play', help=f': Use me to play music ;)')
async def playSong(ctx, *, url = ""):
    voice_channel = ctx.message.author.voice.channel
    if not ctx.message.guild.voice_client:
        await voice_channel.connect()
        voice_channel = ctx.message.guild.voice_client
    else:
        voice_channel = ctx.message.guild.voice_client
    player = await getSong(url)
    voice_channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)

asyncio.run(client.run('MzMxMzMyNzgzODMyMTcwNTA2.GmGUfy.rOaj_NO6YxJl39us1luI3IXGa6JvTfMKoezC_0'))