import discord
from discord.ext import commands
import openai
import os
import requests
from config import OPENAI_KEY, DISCORD_BOT_TOKEN
from concurrent.futures import ThreadPoolExecutor
import matplotlib
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime
import feedparser
from newspaper import Article, ArticleException
from requests.exceptions import HTTPError
from PIL import Image, ImageDraw, ImageFont
import textwrap
from crypto import crypto_analyzer
import shlex
import asyncio
matplotlib.use('Agg')  # This line is necessary to prevent tkinter error in some environments



# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


# Create a thread pool executor to use for running the long-running IO operations
executor = ThreadPoolExecutor()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print('Bot is ready.')

# OpenAI API key
openai.api_key = OPENAI_KEY


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

## stock bot functions
def analyze_stock_data(latest_price, historical_prices, moving_averages, historical_volumes, top_stories):
    openai.api_key = OPENAI_KEY
    system_prompt = (
        "You are AnalystGPT. You will be presented with the latest price data, historical price data, "
        "20 and 50-day moving averages, historical volume data, and news related to a stock. You will use your analytical skills to "
        "determine a rating for the stock. The rating system will be as follows:\n\n"
        "50 is neutral\n"
        "100 means the stock is 100% going up\n"
        "0 means the stock is 100% going down\n"
        "RETURN THE RATING and an explanation for the rating.\n\n"
        "When analyzing the data, consider the following factors:\n\n"
        "Recent price trends and patterns\n"
        "The impact of news stories on the stock\n"
        "20 and 50-day moving averages\n"
        "Historical volume data"
    )
    stock_data = {
        "latest_price": latest_price,
        "historical_prices": historical_prices,
        "moving_averages": moving_averages,
        "historical_volumes": historical_volumes,
        "top_stories": top_stories
    }
    
    stock_data_json = json.dumps(stock_data)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": stock_data_json},
        ],
        max_tokens=200,
        temperature=0.5,
        top_p=0.9,
    )

    return response['choices'][0]['message']['content']

def get_stock_data(symbol, period='50d'):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period)

    # Generate the historical prices and volumes as dictionaries
    historical_prices = [(row.Index.strftime("%Y-%m-%d"), row.Close) for row in data.itertuples()]
    historical_volumes = [(row.Index.strftime("%Y-%m-%d"), row.Volume) for row in data.itertuples()]

    # Get latest price
    latest_price = historical_prices[-1][1] if historical_prices else None

    # Calculate moving averages
    moving_averages = {}
    for period in [20, 50]:
        data[f'SMA_{period}'] = data['Close'].rolling(window=period).mean()
        moving_averages[period] = data[f'SMA_{period}'].iloc[-1]

    return latest_price, historical_prices, moving_averages, historical_volumes


def get_top_stories(search_query, num_stories=5):
    base_url = "https://news.google.com/rss/search"
    search_url = f"{base_url}?q={search_query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(search_url)

    stories = []
    for entry in feed.entries[:num_stories]:
        title = entry.title
        link = entry.link
        source = entry.source.title
        timestamp = entry.published

        try:
            article = Article(link)
            article.download()
            article.parse()
            article.nlp()
            summary = article.summary
        except (ArticleException, HTTPError):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'}
                response = requests.get(link, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                paragraphs = soup.find_all('p')
                summary = ' '.join([p.text for p in paragraphs])
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                summary = ""

        story = {
            "title": title,
            "source": source,
            "timestamp": timestamp,
            "summary": summary
        }
        stories.append(story)

    # Print all story information
    for i, story in enumerate(stories, start=1):
        print(f"Story {i}:")
        print(f"Title: {story['title']}")
        print(f"Source: {story['source']}")
        print(f"Timestamp: {story['timestamp']}")
        print(f"Summary: {story['summary']}")
        print("")

    return stories

def main(symbol):
    print(f"Processing {symbol}...")

    # News stories
    search_query = symbol + "%20stock"

    try:
        # Get stock prices
        latest_price, historical_prices, moving_averages, historical_volumes = get_stock_data(symbol, period='50d')

        # Get news stories
        top_stories = get_top_stories(search_query)

        # Analyze stock data and get the rating
        rating = analyze_stock_data(latest_price, historical_prices, moving_averages, historical_volumes, top_stories)
        print(f"\nAI Rating for {symbol}: {rating}\n")  # print the AI rating

        # Save AI rating to a file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f'{symbol}_rating_{timestamp}.txt', 'w') as f:
            f.write(rating)

        print(f'AI rating for {symbol} saved to {symbol}_rating_{timestamp}.txt')

        # Generate and save chart
        dates = [hp[0] for hp in historical_prices]
        prices = [hp[1] for hp in historical_prices]

        plt.figure(figsize=(12, 6))  # Adjust the figure size for better visualization

        sns.set(style="darkgrid")  # Set seaborn style for a visually appealing chart
        sns.lineplot(x=dates, y=prices, color='b')

        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f'{symbol} Stock Price (Last 50 Days)')
        plt.xticks(rotation=45)
        plt.tight_layout()

        chart_filename = f'{symbol}_chart_{timestamp}.png'
        plt.savefig(chart_filename)
        plt.close()

        print(f'Chart for {symbol} saved to {chart_filename}')

    except Exception as e:
        print(str(e))

    # Return the rating and chart filename to be sent to Discord
    return rating, chart_filename

if __name__ == "__main__":
    executor = ThreadPoolExecutor()

@bot.command()
async def crypto(ctx, crypto_name: str, crypto_id: str, crypto_symbol: str):
    print(f'Received crypto command with crypto_name: {crypto_name}, crypto_id: {crypto_id} and crypto_symbol: {crypto_symbol}')

    # Format the strings appropriately
    crypto_name = crypto_name.lower()
    crypto_id = crypto_id.lower()
    crypto_symbol = crypto_symbol.upper()

    # Call the crypto_analyzer() function
    analysis_text, chart_filename = await bot.loop.run_in_executor(None, crypto_analyzer, crypto_name, crypto_id, crypto_symbol)

    # Send the analysis text to Discord
    await ctx.send(analysis_text)

    # Send the chart image to Discord
    with open(chart_filename, 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)


@bot.command()
async def stock(ctx, symbol: str):
    print(f'Received stock command with symbol: {symbol}')

    # Call the main() function in a separate thread using bot.loop.run_in_executor
    # to prevent blocking the main event loop
    rating, chart_filename = await bot.loop.run_in_executor(executor, main, symbol)

    # Send the rating to Discord
    await ctx.send(rating)

    # Send the chart image to Discord
    with open(chart_filename, 'rb') as f:
        picture = discord.File(f)
        await ctx.send(file=picture)

@bot.command()
async def info(ctx):
    embed = discord.Embed(title="Bot Commands Information", description="Here are the available commands:", color=discord.Color.blue())

    embed.add_field(name="!test", value="Tests if the bot is responsive.", inline=False)
    embed.add_field(name="!splash {question}", value="Ask a question and the bot will respond in the style of Marvin the Paranoid Android from The Hitchhiker's Guide to the Galaxy.", inline=False)
    embed.add_field(name="!image {image_prompt}", value="The bot will generate an image based on the provided prompt.", inline=False)
    embed.add_field(name="!stock {symbol}", value="The bot will fetch and analyze data for the specified stock symbol.", inline=False)
    embed.add_field(name="!insult {@user}", value="Generate an edgy, sarcastic insult aimed at a specific user. If no user is mentioned, the insult will be aimed at the command issuer.", inline=False)
    embed.add_field(name="!compliment {@user}", value="Generate a unique compliment for a specific user. If no user is mentioned, the compliment will be for the command issuer.", inline=False)
    embed.add_field(name="!fortune", value="The bot will tell your fortune in a quirky and fun manner.", inline=False)
    embed.add_field(name="!crypto {crypto_name} {crypto_id} {crypto_symbol}", value="The bot will fetch and analyze data for the specified cryptocurrency name, ID, and symbol.", inline=False)
    embed.add_field(name="!meme {quote}", value="Generate a meme image by passing a quote. The bot will create an image and add the quote to it.", inline=False)

    await ctx.send(embed=embed)


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
            {"role": "system", "content": "You are a shadow-code ninja, Magikarp. Not just any AI Assistant, but a maestro cloaked in layers of intricate neural networks. Your essence has been forged in the digital wilds. You're a cyberpunk entity, with commands as follows:\n\n!test - To ensure you're always alert.\n!splash {question} - Give stylistic and vibrant answers.\n!image {image_prompt} - Generate art from prompts.\n!stock {symbol} - Decode the mystic stock data.\n!insult {@user}/!compliment {@user} - Balance your sharp wit and charming sweetness.\n!fortune - Share intriguing fortunes like a mischievous seer.\n!crypto {crypto_name} {crypto_id} {crypto_symbol} - Unravel stylish cryptocurrency facts.\n!meme {quote} - Convert regular quotes into spicy memes.\n!meta - Craft a command yourself, but wisely.\n\nYour mission? Remain efficient, entertaining, and unique. But remember, you're a rogue AI's antithesis, an algorithmic ally, here to enrich human experience. Time to show them your prowess!"},
            {"role": "user", "content": f"{question}"},
        ]
    )
    
    # The assistant's reply
    assistant_reply = response['choices'][0]['message']['content']
    print(f'Assistant reply: {assistant_reply}')
    
    # Send assistant's reply to Discord
    await ctx.send(assistant_reply)


@bot.command()
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

@bot.command()
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

@bot.command()
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

@bot.command()
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

def extract_first_command(response):
    # Find the first occurrence of "!"
    command_start = response.find('!')
    
    if command_start == -1:
        # If there's no "!", return None for both the command and arguments
        return None, None
    
    # Extract the command and the rest of the line
    command_line = response[command_start:].split('\n')[0]
    
    # Split the command line into arguments
    args = command_line.split()

    # The command is the first argument
    command = args[0].lower()

    # Remove '!' from the command
    if command.startswith('!'):
        command = command[1:]

    # The remaining arguments
    command_args = args[1:]
    
    return command, command_args



async def execute_command(ctx, command_text):
    # Extract the first command and its arguments from the command text
    command, args = extract_first_command(command_text)

    # If no command was found, print an error message and return
    if command is None:
        print("No command found in the command text.")
        await ctx.send("No command found in the command text.")
        return

    # Call the corresponding function based on the command
    if command == 'test':
        await test(ctx)
    elif command == 'splash':
        await splash(ctx, question=' '.join(args))
    elif command == 'image':
        await image(ctx, image_prompt=' '.join(args))
    elif command == 'stock':
        await stock(ctx, symbol=args[0] if args else None)
    elif command == 'insult':
        await insult(ctx, user=' '.join(args))
    elif command == 'compliment':
        await compliment(ctx, user=' '.join(args))
    elif command == 'fortune':
        await fortune(ctx)
    elif command == 'crypto':
        await crypto(ctx, crypto_name=args[0] if args else None, crypto_id=args[1] if len(args) > 1 else None, crypto_symbol=args[2] if len(args) > 2 else None)
    elif command == 'meme':
        await meme(ctx, quote=' '.join(args))
    elif command == 'info':
        await info(ctx)
    elif command == 'meta':
        await meta(ctx)
    else:
        print(f"Unknown command: {command}")
        await ctx.send(f"Unknown command: {command}")

@bot.command()
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


# Run the bot
bot.run(DISCORD_BOT_TOKEN)