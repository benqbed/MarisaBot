from pytube import YouTube
from nextcord.ext import commands
import nextcord
import asyncio

ffmpeg_options = {
    'options': '-vn'
}

client = commands.Bot(command_prefix='>', intents = nextcord.Intents.all())

async def getSong(url):
    yt = YouTube(url)
    filename = yt.streams.desc().first().download()
    return nextcord.FFmpegPCMAudio(source = filename, **ffmpeg_options)

@client.command(name='play', help=f': Use me to play music ;)')
async def playSong(ctx, url = ""):
    voice_channel = ctx.message.author.voice.channel
    await voice_channel.connect()
    voice_channel = ctx.message.guild.voice_client
    player = await getSong(url)
    voice_channel.play(player, after=lambda e: print('Player error: %s' %e) if e else None)

asyncio.run(client.run('MzMxMzMyNzgzODMyMTcwNTA2.GmGUfy.rOaj_NO6YxJl39us1luI3IXGa6JvTfMKoezC_0'))