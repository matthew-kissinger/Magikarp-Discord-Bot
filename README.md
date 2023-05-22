# Magikarp Discord Bot

Magikarp is not your ordinary Discord bot. It's a intelligent bot that comes equipped with several useful features to add a touch of wit and wisdom to your server. Dive into the world of market analysis, creative expression, meme generation, and more with Magikarp!

## Features

- Stock and crypto analysis: Get detailed ratings and charts for stocks and cryptocurrencies.
- Image and meme generation: Create unique images or memes from text prompts using GPT-3.
- Compliments and insults: Dish out customized compliments or sarcastic (but not hurtful) insults to users.
- Fortune telling: Magikarp will reveal your fortune in a quirky and entertaining way.
- Conversation and commands: Engage in various conversations and execute commands using a witty text interface.
- News and stock sentiment analysis: Gather news and StockTwits data on cryptocurrencies and stocks.

## Usage

1. Clone the Repository an navigate to the project directory

```
git clone https://github.com/matthew-kissinger/Magikarp-Discord-Bot.git
cd Magikarp-Discord-Bot
```

2. Install required Python libraries using:

```
pip install -r requirements.txt
```

2. Edit `config.py` to add your own OpenAI API key, Discord bot token, and Custom Search JSON API key:

```python
OPENAI_KEY = "your_openai_api_key_here"
DISCORD_BOT_TOKEN = "your_discord_bot_token_here"
api_key = "your_custom_search_json_api_key_here"
cx = "your_custom_search_cx_here"
```

3. Start the Magikarp bot by running:

```
python magikarp.py
```

4. Once the Magikarp bot is connected to your server, try any of the available commands!

## Commands

* `!test`: Tests if the bot is responsive.
* `!splash {question}`: Asks a question, and the bot will respond in the style of cyber-punk discord bot trained on internet culture.
* `!image {image_prompt}`: Generates an image based on the provided prompt.
* `!stock {symbol}`: Fetches and analyzes data for the specified stock symbol.
* `!insult {@user}`: Generates an edgy, sarcastic insult aimed at a specific user.
* `!compliment {@user}`: Generates a unique compliment for a specific user.
* `!fortune`: Tells your fortune in a quirky and fun manner.
* `!crypto {crypto_name} {crypto_id} {crypto_symbol}`: Fetches and analyzes data for the specified cryptocurrency name, ID, and symbol.
* `!meme {quote}`: Generates a meme image by passing a quote. The bot will create an image and add the quote to it.
* `!meta`: Instructs the bot to generate a random command along with its corresponding input.
* `!info`: Provides general information on the available bot commands.


## Contributing

If you'd like to contribute to the project, feel free to open an issue or create a pull request. 

## License

This project is licensed under the terms of the MIT license. See the [LICENSE.md](LICENSE.md) file for details.
