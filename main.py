import discord
import yaml
from discord.ext import commands

config = yaml.safe_load(open('config.yaml'))
bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    config['prefix']),
    description='A bot to make non Nitro members use non-global Nitro emotes on the servers it is in.',
    pm_help=True)


def load_cog(cog):
    try:
        bot.load_extension(cog)
    except Exception as e:
        print('Could not load cog ' + cog)
        print(e)


@bot.event
async def on_ready():
    print('------------')
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('Using prefix:')
    print(config['prefix'])
    print('------------')
    load_cog('animotes')
    print('Loaded animotes cog...')
    await bot.change_presence(game=discord.Game(name='Use ' + config['prefix'] + 'register to enable me'))

bot.run(config['token'])
