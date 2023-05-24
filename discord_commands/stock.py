import discord
from discord.ext import commands
from core.stock_analysis import main

@commands.command()
async def stock(ctx, symbol: str):
    print(f'Received stock command with symbol: {symbol}')
    rating, chart_filename = await ctx.bot.loop.run_in_executor(None, main, symbol)
    await ctx.send(rating)

    with open(chart_filename, 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)
