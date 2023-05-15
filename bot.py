import discord
from discord.ext import commands
import openai
import os
import requests
from config import OPENAI_KEY, DISCORD_BOT_TOKEN

# Initialize bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print('Bot is ready.')

# OpenAI API key
openai.api_key = OPENAI_KEY

intents = discord.Intents.all() # enables all intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Functions for image generation
def generate_image(image_prompt):
    image_data = openai.Image.create(
        prompt=image_prompt,
        n=1,
        size="1024x1024",
        response_format="url"
    )
    return image_data

def save_image(url, file_path):
    response = requests.get(url)
    response.raise_for_status()  # Ensure we got a successful response

    with open(file_path, 'wb') as f:
        f.write(response.content)

def generate_filename(directory):
    i = 1
    while os.path.exists(f"{directory}/image{i}.png"):
        i += 1
    return f"{directory}/image{i}.png"

@bot.command()
async def test(ctx):
    print("Test command received.")
    await ctx.send("Test command received!")

@bot.command()
async def splash(ctx, *, question):
    print(f'Received command with question: {question}')
    
    # User message to OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Adjust model output behavior to mirror the characteristics of Hitchhiker's Guide to the Galaxy's Marvin the Paranoid Android, known for his gloomy, pessimistic, and sarcastically humorous outlook. The responses should be tinged with dry wit and a seemingly perpetual sense of despondency. Avoid revealing any explicit details that could identify the source character. Maintain an air of intelligence and advanced understanding, but pair this with a general sense of dissatisfaction and a humorous, if slightly bleak, perspective on existence."},
            {"role": "user", "content": f"{question}"},
        ]
    )
    
    # The assistant's reply
    assistant_reply = response['choices'][0]['message']['content']
    print(f'Assistant reply: {assistant_reply}')
    
    # Send assistant's reply to Discord
    await ctx.send(assistant_reply)

@bot.command()
async def image(ctx, *, image_prompt):
    print(f'Received image command with prompt: {image_prompt}')

    # Generate the raw response
    response = generate_image(image_prompt)

    # Extract the image URL from the response
    image_url = response['data'][0]['url']

    # Generate the filename
    filename = generate_filename(os.getcwd())

    # Save the image to a local file
    save_image(image_url, filename)

    print(f"Image saved as '{filename}'.")
    
    # Send the image to Discord
    with open(filename, 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)

# Run the bot
bot.run(DISCORD_BOT_TOKEN)

