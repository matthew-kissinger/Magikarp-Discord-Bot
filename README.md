# Magikarp Discord Bot

Magikarp is an AI-driven Discord bot with a unique twist. Inspired by Marvin the Paranoid Android from Hitchhiker's Guide to the Galaxy, it interacts with users in a style that combines dry wit and a dash of pessimism.

## Features

1. **Text Generation**: Utilizing OpenAI's advanced GPT-3.5 chat model, Magikarp can generate responses to a wide range of prompts. Whether you're asking a serious question or looking for a humorous conversation, Magikarp has got you covered.

2. **Image Generation**: Need a picture of a futuristic city? Or a cartoon version of a cat? Magikarp can generate it for you with OpenAI's Image API.

3. **Test Command**: Use the `!test` command to ensure Magikarp is operational.

4. **Stock Analysis**: Get GPT-3.5 chat model to do stock analysis using latest price, historical prices and volumes, and recent news stories to produce a rating and stock chart.

## How to Use

1. Clone the repository.
2. Replace `'your_openai_key_here'` and `'your_discord_bot_token_here'` in `config.py` with your OpenAI API key and Discord bot token.
3. Run the bot.

Here are the commands you can use:

- `!splash [your question]`: Ask a question or initiate a conversation.
- `!image [your image prompt]`: Generate an image based on the given prompt.
- `!test`: Confirm the bot's presence and functionality.
- '!stock' [Ticker Symbol]': Real-time stock analysis and chart creation

Please note, Magikarp is a bit of a pessimist, but always ready to help!

## Requirements

- Python
- discord.py library
- OpenAI API key
- Discord bot token

## Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for details.

## License

This project is licensed under the terms of the MIT license. See `LICENSE.md` for details.
