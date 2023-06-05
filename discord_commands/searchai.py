import asyncio
from discord.ext import commands
from core.search import prospect

@commands.command()
async def search(ctx, *args):
    if len(args) > 1 and args[-1].isdigit():
        rounds = int(args[-1])  # last argument is the number of rounds if it's a number
        name = ' '.join(args[:-1])  # all previous arguments form the name
    else:
        rounds = 2  # default number of rounds
        name = ' '.join(args)  # all arguments form the name

    print(f'Received search command with name: {name} and rounds: {rounds}')
    profile = await asyncio.get_event_loop().run_in_executor(None, prospect, name, rounds)

    # Split message into chunks to respect Discord's limit
    for chunk in [profile[i:i+2000] for i in range(0, len(profile), 2000)]:
        await ctx.send(chunk)
