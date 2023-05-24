from discord.ext import commands
from core.image_gen import generate_image, save_image, generate_filename
import openai
import discord
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont


@commands.command()
async def meme(ctx, *, quote):
    print(f'Received meme command with quote: {quote}')

    # Convert quote to uppercase
    quote = quote.upper()

    # Using GPT-3.5-turbo to get a description for the image from the quote
    prompt = f"Generate a description for an image that fits this quote with no more than 25 words and only return the description: \"{quote}\""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )
    image_description = response['choices'][0]['message']['content']

    # Generating an image from the description
    image_response = generate_image(image_description)
    image_url = image_response['data'][0]['url']
    filename = generate_filename(os.getcwd())
    save_image(image_url, filename)

    # Open the image file with Pillow
    img = Image.open(filename)
    draw = ImageDraw.Draw(img)

    # Get the width and height of the image
    img_width, img_height = img.size

    # Determine the width of the text block, keeping some margins
    text_width = img_width * 0.9  # 90% of the image width

    # Initially set the maximum font size
    font_size = 60

    # Create a loop to progressively decrease the font size until the text fits the image
    while True:
        # Create the font object
        font = ImageFont.truetype('impact.ttf', size=font_size)

        # Estimate the number of characters per line and the number of lines
        chars_per_line = text_width // font.getsize('A')[0]  # assuming 'A' is representative
        lines = textwrap.wrap(quote, width=chars_per_line)

        # Check if the text height fits the image
        text_height = len(lines) * font.getsize('A')[1]  # assuming 'A' is representative
        if text_height < img_height * 0.9:  # 90% of the image height
            break

        # If the text doesn't fit, decrease the font size and try again
        font_size -= 1

    # Now use this `lines` list and `font` object for your text rendering

    y_text = 10
    stroke_width = 2  # Define stroke width
    stroke_fill = "black"  # Define stroke color
    for line in lines:
        line_width, line_height = font.getsize(line)
        x = (img.width - line_width) / 2
        # Draw the stroke
        for adj in range(stroke_width):
            draw.text((x-adj, y_text), line, font=font, fill=stroke_fill)
            draw.text((x+adj, y_text), line, font=font, fill=stroke_fill)
            draw.text((x, y_text-adj), line, font=font, fill=stroke_fill)
            draw.text((x, y_text+adj), line, font=font, fill=stroke_fill)
        # Draw the text
        draw.text((x, y_text), line, font=font, fill="white")
        y_text += line_height

    # Save the edited image
    img.save(filename)

    # Send the meme to Discord
    with open(filename, 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)
