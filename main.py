import discord
from discord.ext import commands
from discord_commands.general import rpg,continue_rpg_game, test, info, splash, compliment, insult, fortune, meta
from discord_commands.crypto import crypto
from discord_commands.stock import stock
from discord_commands.image import image
from discord_commands.meme import meme
from discord_commands.searchai import search
from config import DISCORD_BOT_TOKEN

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


bot.add_command(test)
bot.add_command(info)
bot.add_command(splash)
bot.add_command(compliment)
bot.add_command(insult)
bot.add_command(fortune)
bot.add_command(crypto)
bot.add_command(stock)
bot.add_command(meta)
bot.add_command(image)
bot.add_command(meme)
bot.add_command(rpg)
bot.add_command(search)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print('Bot is ready.')

@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author.bot:
        return

    if message.reference is not None and message.reference.resolved.author.id == bot.user.id:
        # This is a reply to a bot message, continue the RPG game
        await continue_rpg_game(message.channel, message)
    elif message.content.startswith('!'):
        # This is a command, parse and invoke it
        cmd_name, *args = message.content.split()
        cmd = bot.get_command(cmd_name[1:])
        if cmd:
            await cmd(message.channel, *args)


# Run the bot
bot.run(DISCORD_BOT_TOKEN)
