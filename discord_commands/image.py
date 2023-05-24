import discord
import os
from discord.ext import commands
from core.image_gen import generate_image, save_image, generate_filename

@commands.command()
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