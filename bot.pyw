from discord import File
from discord.ext import commands

from formatResponses import format_build, format_runas, format_commands, format_last_update
from lolRunas import get_runas, get_progression, get_best_champs, get_build_champ, get_last_update

token = 'your discord token here'
symbol = '$'
client = commands.Bot(command_prefix=symbol)

commands = ['commands',
            'runas [campeãoTudoJunto] (lane)',
            'progression (X) - Top X com a maior variação da % de vitórias',
            'best - Campeões com maior winrate',
            'build [campeãoTudoJunto]',
            'lastUpdate - Imagem com resumo da ultima att']

additionals = ['(entre parenteses) -> opcional']
git_hub_link = 'https://github.com/BeTToH/LoL-Discord-Bot'


@client.event
async def on_ready():
    channel = client.get_channel(608804696345280533)
    await channel.send("Robert Bot :robot:  tá on, nerds!")


@client.command(name='runas')
async def runas(ctx, msg):
    async with ctx.typing():
        msg = msg.replace('$runas ', '').lower().split(' ')
        lane = ""
        if len(msg) > 1:
            lane = msg[1]
        champ = msg[0]
        runas, winrate = await get_runas(champ, lane)
        if runas != '':
            response = format_runas(champ, lane, runas, winrate)
            with open('img.png', 'rb') as f:
                picture = File(f)
                await ctx.send(response, file=picture, tts=False)


@client.command(name='runa')
async def runas2(ctx, msg):
    async with ctx.typing():
        try:
            msg = msg.replace('$runas ', '').lower().split(' ')
            lane = ""
            if len(msg) > 1:
                lane = msg[1]
            champ = msg[0]
            runas, winrate = await get_runas(champ, lane)
            if runas != '':
                response = format_runas(champ, lane, runas, winrate)
                with open('img.png', 'rb') as f:
                    picture = File(f)
                    await ctx.send(response, file=picture, tts=False)
        except:
            await ctx.send('ERRO!')


@client.command(name='progression')
async def progression(ctx, msg=''):
    async with ctx.typing():
        if msg != '':
            if msg.isnumeric():
                response = str(await get_progression(msg))
                response = '```\n' + response + '\n```'
            else:
                response = 'ERRO! Insira um valor válido para x.'
        else:
            response = str(await get_progression())
            response = '```\n' + response + '\n```'
        await ctx.send(response)


@client.command(name='best')
async def best(ctx):
    async with ctx.typing():
        response = str(await get_best_champs())
        response = response.replace('\n', '').replace('#', '\n')
        response = '```\n' + response + '\n```'
        await ctx.send(response, tts=False)


@client.command(name='build')
async def build(ctx, msg=""):
    async with ctx.typing():
        if msg != '' and msg.isalpha():
            msg = msg.replace('$runas ', '').lower().split(' ')
            if len(msg) == 2:
                build = await get_build_champ(msg[0], msg[1])
            else:
                build = await get_build_champ(msg[0])
            response = format_build(msg[0], build)
        else:
            response = "Insira no formato correto! Digite $commands para mais informações."
        await ctx.send(embed=response, tts=False)


@client.command(name='lastUpdate')
async def get_last_updat(ctx):
    async with ctx.typing():
        img_link, num_att = await get_last_update()
        response = format_last_update(img_link, num_att)
        await ctx.send(embed=response)


@client.command(name='commands')
async def coms(ctx):
    async with ctx.typing():
        response = format_commands(symbol, commands)
        await ctx.send(embed=response, tts=False)


client.run(token)
