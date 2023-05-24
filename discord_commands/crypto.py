import openai
from config import OPENAI_KEY
from core.crypto_analysis import crypto_analyzer
import discord
from discord.ext import commands
import asyncio

@commands.command()
async def crypto(ctx, crypto_name: str, crypto_id: str, crypto_symbol: str):
    print(f'Received crypto command with crypto_name: {crypto_name}, crypto_id: {crypto_id} and crypto_symbol: {crypto_symbol}')

    # Format the strings appropriately
    crypto_name = crypto_name.lower()
    crypto_id = crypto_id.lower()
    crypto_symbol = crypto_symbol.upper()

    # Call the crypto_analyzer() function
    loop = asyncio.get_event_loop()
    analysis_text, chart_filename = await loop.run_in_executor(None, crypto_analyzer, crypto_name, crypto_id, crypto_symbol)

    # Send the analysis text to Discord
    await ctx.send(analysis_text)

    # Send the chart image to Discord
    with open(chart_filename, 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)
