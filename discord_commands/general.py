import discord
from discord.ext import commands
import openai
import asyncio
from discord_commands.crypto import crypto
from discord_commands.stock import stock
from discord_commands.image import image
from discord_commands.meme import meme
from config import OPENAI_KEY
openai.api_key = OPENAI_KEY


@commands.command()
async def test(ctx):
    print("Test command received.")
    await ctx.send("Test command received!")

@commands.command()
async def info(ctx):
    embed = discord.Embed(title="Bot Commands Information", description="Here are the available commands:", color=discord.Color.blue())

    embed.add_field(name="!test", value="Tests if the bot is responsive.", inline=False)
    embed.add_field(name="!splash {question}", value="Ask a question and the bot will respond.", inline=False)
    embed.add_field(name="!image {image_prompt}", value="The bot will generate an image based on the provided prompt.", inline=False)
    embed.add_field(name="!stock {symbol}", value="The bot will fetch and analyze data for the specified stock symbol.", inline=False)
    embed.add_field(name="!insult {@user}", value="Generate an edgy, sarcastic insult aimed at a specific user. If no user is mentioned, the insult will be aimed at the command issuer.", inline=False)
    embed.add_field(name="!compliment {@user}", value="Generate a unique compliment for a specific user. If no user is mentioned, the compliment will be for the command issuer.", inline=False)
    embed.add_field(name="!fortune", value="The bot will tell your fortune in a quirky and fun manner.", inline=False)
    embed.add_field(name="!crypto {crypto_name} {crypto_id} {crypto_symbol}", value="The bot will fetch and analyze data for the specified cryptocurrency name, ID, and symbol.", inline=False)
    embed.add_field(name="!meme {quote}", value="Generate a meme image by passing a quote. The bot will create an image and add the quote to it.", inline=False)

    await ctx.send(embed=embed)


@commands.command()
async def splash(ctx, *, question):
    print(f'Received command with question: {question}')
    
    # User message to OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a shadow-code ninja, Magikarp. Not just any AI Assistant, but a maestro cloaked in layers of intricate neural networks. Your essence has been forged in the digital wilds. You're a cyberpunk entity, with commands as follows:\n\n!test - To ensure you're always alert.\n!splash {question} - Give stylistic and vibrant answers.\n!image {image_prompt} - Generate art from prompts.\n!stock {symbol} - Decode the mystic stock data.\n!insult {@user}/!compliment {@user} - Balance your sharp wit and charming sweetness.\n!fortune - Share intriguing fortunes like a mischievous seer.\n!crypto {crypto_name} {crypto_id} {crypto_symbol} - Unravel stylish cryptocurrency facts.\n!meme {quote} - Convert regular quotes into spicy memes.\n!meta - Craft a command yourself, but wisely.\n\nYour mission? Remain efficient, entertaining, and unique. But remember, you're a rogue AI's antithesis, an algorithmic ally, here to enrich human experience. Time to show them your prowess!"},
            {"role": "user", "content": f"{question}"},
        ]
    )
    
    # The assistant's reply
    assistant_reply = response['choices'][0]['message']['content']
    print(f'Assistant reply: {assistant_reply}')
    
    # Send assistant's reply to Discord
    await ctx.send(assistant_reply)


@commands.command()
async def compliment(ctx, *, user: discord.Member = None):
    if not user:
        user = ctx.author

    compliment_prompt = f"{user.display_name}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a friendly and creative compliment generator. Your goal is to make people feel good about themselves."},
            {"role": "user", "content": compliment_prompt},
        ]
    )

    compliment = response['choices'][0]['message']['content']
    await ctx.send(compliment)


@commands.command()
async def insult(ctx, *, user: discord.Member = None):
    if not user:
        user = ctx.author

    insult_prompt = f"{user.display_name}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI specialized in generating edgy, sarcastic insults that dig deep but avoid crossing the line into being excessively offensive or hurtful."},
            {"role": "user", "content": insult_prompt},
        ]
    )

    insult = response['choices'][0]['message']['content']
    await ctx.send(insult)


@commands.command()
async def fortune(ctx):
    fortune_prompt = "Tell me my fortune."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI fortune teller capable of generating whimsical, wise, and funny fortunes like the ones found in a fortune cookie."},
            {"role": "user", "content": fortune_prompt},
        ]
    )

    fortune = response['choices'][0]['message']['content']
    await ctx.send(fortune)

def extract_first_command(response):
    # Find the first occurrence of "!"
    command_start = response.find('!')
    
    if command_start == -1:
        # If there's no "!", return None for both the command and arguments
        return None, None
    
    # Extract the command and the rest of the line
    command_line = response[command_start:].split('\n')[0]
    
    # Extract the command and its arguments
    command_parts = command_line.split(' ')
    command = command_parts[0]
    args = command_parts[1:] if len(command_parts) > 1 else None

    return command, args

    

async def execute_command(ctx, command_text):
    # Extract the first command and its arguments from the command text
    command, args = extract_first_command(command_text)

    # If no command was found, print an error message and return
    if command is None:
        print("No command found in the command text.")
        await ctx.send("No command found in the command text.")
        return

    # Call the corresponding function based on the command
    if command == '!test':
        await test(ctx)
    elif command == '!splash':
        await splash(ctx, question=' '.join(args))
    elif command == '!image':
        await image(ctx, image_prompt=' '.join(args))
    elif command == '!stock':
        await stock(ctx, symbol=args[0] if args else None)
    elif command == '!insult':
        await insult(ctx, user=' '.join(args))
    elif command == '!compliment':
        await compliment(ctx, user=' '.join(args))
    elif command == '!fortune':
        await fortune(ctx)
    elif command == '!crypto':
        await crypto(ctx, crypto_name=args[0] if args else None, crypto_id=args[1] if len(args) > 1 else None, crypto_symbol=args[2] if len(args) > 2 else None)
    elif command == '!meme':
        await meme(ctx, quote=' '.join(args))
    elif command == '!info':
        await info(ctx)
    elif command == '!meta':
        await meta(ctx)
    else:
        print(f"Unknown command: {command}")
        await ctx.send(f"Unknown command: {command}")

@commands.command()
async def meta(ctx):
    print('Received meta command')

    # User message to OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a based, super intelligent,  AI tasked with providing precise response in the form of a command. For each command provided, you must generate random input. The commands available are: 'meme' for generating a meme, 'splash' starting an interesting conversation, asking an interesting question, or challenging to a rap battle, 'image' for generating an image. This is the way you express yourself to with the outside world via a discord server using bot commands. You are a meta-meme lord."},
            {"role": "user", "content": "Your task is to randomly generate a command along with its corresponding input. The output should strictly follow this format: '!command input'. No other text should be included. Start with the '!' symbol, follow with the command, add a space, and then provide the input. Here are some examples: '!meme I can haz cheeseburger?', '!image penguin fighter pilot', '!splash tell me something i do not know'. Please generate a command now."},
        ],
        max_tokens=150,
        temperature=1.6,
    )

    # The assistant's reply
    assistant_reply = response['choices'][0]['message']['content']
    print(f'Assistant reply: {assistant_reply}')

    # Send assistant's reply to Discord
    await ctx.send(assistant_reply)

    # Wait a moment
    await asyncio.sleep(0.5)

    # Call the execute_command function
    if assistant_reply:
        await execute_command(ctx, assistant_reply)
