import discord
from discord.ext import commands
import openai
import asyncio
import json
import re
import os
from discord import File
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
    embed.add_field(name="!rpg {location} {initial_scenario}", value="Start a new RPG game. Provide a location and initial scenario. For example, !rpg 'Castle' 'a dragon is attacking the castle'. After starting a game with !rpg, the AI will provide a series of potential actions. Input one of these actions to continue the game. The AI will maintain a game state and generate a narrative based on your actions. You can end the game at any time by typing 'exit'.", inline=False)

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
            {"role": "system", "content": "You are a based, super intelligent,  AI tasked with providing precise response in the form of a command. For each command provided, you must generate random input. The commands available are: 'meme' for generating a meme, 'splash' starting an interesting conversation, asking an interesting question, or anything that warrants a response, 'image' for generating an image. This is the way you express yourself to with the outside world via a discord server using bot commands. You are a meta-meme lord."},
            {"role": "user", "content": "Your task is to randomly generate a command along with its corresponding input. The output should strictly follow this format: '!command input'. No other text should be included. Start with the '!' symbol, follow with the command, add a space, and then provide the input. Here are some examples: '!meme I can haz cheeseburger?', '!image penguin fighter pilot', '!splash tell me something i do not know'. The meme command is your go to command. Please generate a command now."},
        ],
        max_tokens=150,
        temperature=1.2,
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

user_history = []
ai_history = []
system_prompt = """
Your instructions as an AI Dungeon Master for a text-based RPG involve both maintaining the game state as well as generating a context-driven narrative for each turn. When the player makes a decision, this should be reflected in the updated game state, and the narrative should also change to reflect their actions. This dynamic gameplay narrative will help immerse the player in the game.

Here's how this works:

To maintain the game state, you need to update the JSON structures as per the player's actions. For example, if the player chooses to explore, they may gain experience points, new items, and potentially encounter significant events. All of this will be reflected in the game state.

The narrative is the AI's description of the game world and the player's actions within it. It sets the scene for the player, describing the environment, the player's status, and their available options.

Here's an example of how a game might unfold:

AI MESSAGE:

{
"turn": "1",
"time": "midnight",
"day": "Day 1",
"weather": "rainy",
"health": 100,
"xp": 0,
"level": 1,
"location": "Shadow City",
"gold": 200,
"inventory": ["magic wand", "cloak of invisibility", "healing potion", "spellbook", "mooncake"],
"quest": "Rescue the Starlight Princess",
"attributes": {"magic power": 20, "speed": 18, "wisdom": 16, "endurance": 14, "charm": 14},
"turnHistory": [],
"initialScenario": "wizard preparing for a midnight feast",
"significantEvents": []
}

Narrative: "You stand in the mystical alleys of Shadow City, the midnight rain dripping off your cloak of invisibility. As you prepare for a moonlit feast, a mystical raven delivers a message about the Starlight Princess being kidnapped. Your quest - Rescue the Starlight Princess - begins."

{
"actions": ["explore", "sleep", "cast spell", "travel"]
}

PLAYER MESSAGE:
explore

AI MESSAGE:

{
"turn": "2",
"time": "late midnight",
"day": "Day 1",
"weather": "rainy",
"health": 100,
"xp": 7,
"level": 1,
"location": "Shadow City Marketplace",
"gold": 200,
"inventory": ["magic wand", "cloak of invisibility", "healing potion", "spellbook", "mooncake"],
"quest": "Rescue the Starlight Princess",
"attributes": {"magic power": 20, "speed": 18, "wisdom": 16, "endurance": 14, "charm": 14},
"turnHistory": ["e1: explored Shadow City"],
"initialScenario": "wizard preparing for a midnight feast",
"significantEvents": ["Encountered Shadow Thief"],
}

Narrative: "Continuing your exploration of Shadow City, you arrive at the bustling marketplace. Suddenly, a mysterious figure emerges from the shadows – a Shadow Thief! With all your senses heightened, you face your new foe. Will you fight, flee, cast a spell or try to negotiate with this enemy?"

{
"actions": ["fight", "flee", "cast spell", "negotiate"]
}

Remember to update the game state and narrative based on the player's previous actions, change the actions based on the current narrative, and start each response with the game state followed by the narrative.
"""

@commands.command()
async def rpg(ctx, *args):
    # Parse the args. The first word is the location, and the rest is the initial scenario.
    location = args[0]
    initial_scenario = " ".join(args[1:])
    start_game_message = f"Create a new game state using {location} as the location and {initial_scenario} as the initial scenario. Respond with the first AI MESSAGE."

    # Clear AI and user message history
    user_history.clear()
    ai_history.clear()

    # Combine system_prompt and start_game_message
    full_prompt = system_prompt + " " + start_game_message

    # Generate the initial AI response
    response = generate_response(full_prompt)

    # Parse the initial response
    ai_message = response['choices'][0]['message']['content']

    # Store the unmodified ai_message
    store_message(ai_message, sender="ai")

    # Extract the first outermost JSON string by counting brackets
    brackets = 0
    json_start = ai_message.find('{')
    for i, c in enumerate(ai_message[json_start:]):
        if c == '{':
            brackets += 1
        elif c == '}':
            brackets -= 1
        if brackets == 0:
            json_end = i + json_start
            break

    json_string_1 = ai_message[json_start:json_end+1]

    # Parse the first JSON string and save as a file
    game_state = json.loads(json_string_1)
    with open('game_state.json', 'w') as f:
        json.dump(game_state, f)

    # Remove the first JSON string from ai_message and strip whitespace
    ai_message = ai_message.replace(json_string_1, "").strip()

    # Extract the narrative part using regex (text following the word "Narrative:" and ending before the start of the next JSON string)
    narrative_part = re.search(r'Narrative:(.*?)\{', ai_message, re.DOTALL)
    if narrative_part:
        narrative_part = narrative_part.group(1).strip()

    # Extract the second outermost JSON string (for the Embed)
    brackets = 0
    json_start = ai_message.find('{')
    for i, c in enumerate(ai_message[json_start:]):
        if c == '{':
            brackets += 1
        elif c == '}':
            brackets -= 1
        if brackets == 0:
            json_end = i + json_start
            break

    json_string_2 = ai_message[json_start:json_end+1]

    # Parse second JSON for the Embed
    embed_json = json.loads(json_string_2)

    # Check if embed_json has 'actions' key to be used as an Embed
    if 'actions' in embed_json:
        embed = discord.Embed(title="Actions", description="\n".join(embed_json['actions']))

        # Create a discord.File object from the game state file
        game_state_file = File('game_state.json')

        # Send the narrative part, the Embed, and then the game state file
        await ctx.send(narrative_part)
        await ctx.send(embed=embed)
        await ctx.send(file=game_state_file)

        # Delete the game_state.json file after sending it
        os.remove('game_state.json')
    else:
        print('Invalid Embed: ', embed_json)



async def continue_rpg_game(ctx, message):
    player_message = message.content

    # Generate response based on the player's message
    response = generate_response(player_message)

    # Store the unmodified ai_message
    ai_message = response['choices'][0]['message']['content']
    store_message(ai_message, sender="ai")

    # Extract the first outermost JSON string by counting brackets
    brackets = 0
    json_start = ai_message.find('{')
    for i, c in enumerate(ai_message[json_start:]):
        if c == '{':
            brackets += 1
        elif c == '}':
            brackets -= 1
        if brackets == 0:
            json_end = i + json_start
            break

    json_string_1 = ai_message[json_start:json_end+1]

    # Parse the first JSON string and save as a file
    game_state = json.loads(json_string_1)
    with open('game_state.json', 'w') as f:
        json.dump(game_state, f)

    # Remove the first JSON string from ai_message and strip whitespace
    ai_message = ai_message.replace(json_string_1, "").strip()

    # Extract the narrative part using regex (text following the word "Narrative:" and ending before the start of the next JSON string)
    narrative_part = re.search(r'Narrative:(.*?)\{', ai_message, re.DOTALL)
    if narrative_part:
        narrative_part = narrative_part.group(1).strip()

    # Extract the second outermost JSON string (for the Embed)
    brackets = 0
    json_start = ai_message.find('{')
    for i, c in enumerate(ai_message[json_start:]):
        if c == '{':
            brackets += 1
        elif c == '}':
            brackets -= 1
        if brackets == 0:
            json_end = i + json_start
            break

    json_string_2 = ai_message[json_start:json_end+1]

    # Parse second JSON for the Embed
    embed_json = json.loads(json_string_2)

    # Check if embed_json has 'actions' key to be used as an Embed
    if 'actions' in embed_json:
        embed = discord.Embed(title="Actions", description="\n".join(embed_json['actions']))

        # Create a discord.File object from the game state file
        game_state_file = File('game_state.json')

        # Send the narrative part, the Embed, and then the game state file
        await ctx.send(narrative_part)
        await ctx.send(embed=embed)
        await ctx.send(file=game_state_file)

        # Delete the game_state.json file after sending it
        os.remove('game_state.json')
    else:
        print('Invalid Embed: ', embed_json)

    # Store the user's message and remove old messages if needed
    store_message(message.content, sender="user")


def generate_response(message):
    user_history.append({"role": "user", "content": message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            *ai_history[-5:],
            *user_history[-5:],
        ]
    )
    return response

def store_message(message, sender):
    if sender == "user":
        user_history.append({"role": "user", "content": message})
        if len(user_history) > 5:
            user_history.pop(0)
    elif sender == "ai":
        ai_history.append({"role": "assistant", "content": message})
        if len(ai_history) > 5:
            ai_history.pop(0)