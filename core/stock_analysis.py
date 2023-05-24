import openai
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
from config import OPENAI_KEY
import requests

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