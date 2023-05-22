# Magikarp Discord Bot

Magikarp, the most powerful (and quirky) Discord bot you'll ever meet, powered by OpenAI API and some python magic.

## Requirements
- OpenAI API Key
- Custom Search JSON API*
- Python

*only required for !crypto command

## Features

Magikarp has a wide array of functionalities, including:

- Responding to questions in the style of Marvin the Paranoid Android from The Hitchhiker's Guide to the Galaxy.
- Generating images based on prompts.
- Fetching and analyzing data and news for specified stocks.
- Fetching and analyzing data, news, and social media posts for specified crypto.
- Delivering edgy, sarcastic insults.
- Producing unique compliments.
- Telling fortunes in a quirky and fun manner.
- Making memes.

## Commands

- `!test`: Tests if the bot is responsive.
- `!splash {question}`: Ask a question and the bot will respond in the style of Marvin the Paranoid Android from The Hitchhiker's Guide to the Galaxy.
- `!image {image_prompt}`: The bot will generate an image based on the provided prompt.
- `!stock {symbol}`: The bot will fetch and analyze data for the specified stock symbol.
- `!insult {@user}`: Generate an edgy, sarcastic insult aimed at a specific user. If no user is mentioned, the insult will be aimed at the command issuer.
- `!compliment {@user}`: Generate a unique compliment for a specific user. If no user is mentioned, the compliment will be for the command issuer.
- `!fortune`: The bot will tell your fortune in a quirky and fun manner.
- `!meme {quote}`: The bot will create a meme with your quote in impact font.
- `!crypto {crypto_name} {crypto_symbol}`:The bot will fetch and analyze data for the specified cryptocurrency name and symbol.

## Usage

You can use Magikarp by inviting it to your server and typing `!<command>` in any text channel. You can replace `<command>` with any of the commands listed above.

## Development

Magikarp was developed using Python and the discord.py library, with natural language processing powered by OpenAI's GPT-3.5-turbo. 

## Set Up Your Own Google Custom Search Engine

In order to use this application, you will need to set up your own Google Custom Search Engine (CSE) and get a JSON API key. Here are the steps to do so:

### 1. Create a Google Custom Search Engine

First, visit [Google's Custom Search Engine](https://cse.google.com/cse/all) page and sign in with your Google account. Then, follow the steps to create a new search engine:

- Click on "New Search Engine".
- In the "Sites to search" section, add the following sites:
'''
www.coindesk.com/*
.cryptonews.com/
.coinledger.io/
.cointelegraph.com/
.crypto.news/
.nulltx.com/
.todayonchain.com/
news.google.com/*
www.bbc.com/news/*
www.cnn.com/*
www.reuters.com/*
www.bloomberg.com/*
www.nytimes.com/*
'''
- Click on "Create".


### 2. Get JSON API Key

Next, visit [Google Cloud Console](https://console.cloud.google.com/) and create a new project. After the project is created, follow the steps below:

- Navigate to "Credentials" under "APIs & Services".
- Click "Create credentials" and select "API Key".
- After the API Key is generated, restrict the key to the "Custom Search JSON API".
- Click "Save".

You now have your Google CSE ID and the API Key which can be used to integrate the custom search into your application.

Please remember to keep your API key secret and do not expose it in any public repository or version control system as it could be misused.



## Contributing

If you'd like to contribute to the project, feel free to open an issue or create a pull request. 

## License

This project is licensed under the terms of the MIT license. See the [LICENSE.md](LICENSE.md) file for details.
