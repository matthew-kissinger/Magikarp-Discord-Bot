import discord
from discord.ext import commands
from discord_commands.general import test, info, splash, compliment, insult, fortune, meta
from discord_commands.crypto import crypto
from discord_commands.stock import stock
from discord_commands.image import image
from discord_commands.meme import meme
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

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print('Bot is ready.')


# Run the bot
bot.run(DISCORD_BOT_TOKEN)
