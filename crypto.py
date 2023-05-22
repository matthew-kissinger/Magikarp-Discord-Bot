import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json
import re
import openai
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import config



def generate_filename(crypto, base_filename):
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{crypto}_{current_datetime}_{base_filename}"
    return filename

def analyze_crypto_data(report_text, filename):
    openai.api_key = config.OPENAI_KEY
    system_prompt = (
        "You are CryptoAnalystGPT. You will be presented with the latest price data, historical price data, "
        "moving averages, historical volume data, news related to a cryptocurrency, and stock twits posts. You will use your analytical skills to "
        "determine a rating for the cryptocurrency. The rating system will be as follows:\n\n"
        "50 is neutral\n"
        "100 means the cryptocurrency is 100% going up\n"
        "0 means the cryptocurrency is 100% going down\n"
        "RETURN THE RATING and an explanation for the rating.\n\n"
        "When analyzing the data, consider the following factors:\n\n"
        "Recent price trends and patterns\n"
        "The impact of news stories on the cryptocurrency\n"
        "Moving averages\n"
        "Social sentiment\n"
        "Historical volume data"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": report_text},
        ],
        max_tokens=400,
        temperature=0.5,
        top_p=0.9,
    )

    analysis = response['choices'][0]['message']['content']
    
    # Write analysis to the file
    with open(filename, 'a') as f:
        f.write(f"Analysis:\n{analysis}\n\n")
    
    return analysis


def get_coin_data(crypto, chart_filename):
    url_market_chart = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days=21"
    url_coin_data = f"https://api.coingecko.com/api/v3/coins/{crypto}"

    response_market_chart = requests.get(url_market_chart)
    data_market_chart = response_market_chart.json()

    response_coin_data = requests.get(url_coin_data)
    data_coin_data = response_coin_data.json()

    df = pd.DataFrame({
        'time': [i[0] for i in data_market_chart['prices']],
        'price': [i[1] for i in data_market_chart['prices']],
        'volume': [i[1] for i in data_market_chart['total_volumes']]
    })

    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)
    df['price'] = df['price'].astype(float)
    df['volume'] = df['volume'].astype(float)
    df = df.resample('D').mean()  

    # Calculate SMA and RSI
    df['SMA'] = df['price'].rolling(window=5).mean()
    delta = df['price'].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    avg_gain = up.rolling(window=14).mean()
    avg_loss = abs(down.rolling(window=14).mean())
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # Keep only the last 7 days of data
    df = df.last('7D')

    # Plotting data
    fig, ax1 = plt.subplots(figsize=(10, 5))  # specify figure size

    ax1.set_xlabel('Time (days)')
    ax1.set_ylabel('Price ($)', color='tab:blue')
    ax1.plot(df.index, df['price'], color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()  
    ax2.set_ylabel('Volume', color='tab:red')  
    ax2.bar(df.index, df['volume'], color='tab:red', alpha=0.3)  # Changed from ax2.plot to ax2.bar
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # Format x-axis to show only month and day
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))

    fig.tight_layout()  
    plt.title(f"{crypto} price and volume over the last 7 days")
    
    # Save figure
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    plt.savefig(chart_filename)

    week_high_price = round(df['price'].max(), 3)
    week_low_price = round(df['price'].min(), 3)
    week_high_volume = round(df['volume'].max(), 3)
    week_low_volume = round(df['volume'].min(), 3)

    all_time_high_price = round(data_coin_data['market_data']['ath']['usd'], 3)
    all_time_low_price = round(data_coin_data['market_data']['atl']['usd'], 3)

    report = f"Cryptocurrency: {crypto}\n"
    report += f"All time high price: ${all_time_high_price}\n"
    report += f"All time low price: ${all_time_low_price}\n"
    report += f"Week high price: ${week_high_price}\n"
    report += f"Week low price: ${week_low_price}\n"
    report += f"Week high volume: ${week_high_volume}\n"
    report += f"Week low volume: ${week_low_volume}\n"

    return report


def search_articles(crypto_name, api_key, cx, start_index):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": f"{crypto_name} news",
        "key": api_key,
        "cx": cx,
        "sort": "date",
        "num": 10,
        "start": start_index
    }
    response = requests.get(url, params=params)
    return response.json()

def get_crypto_news(crypto_name, api_key, cx):
    start_index = 1
    articles_found = 0
    news_report = ""

    while articles_found < 10:
        data = search_articles(crypto_name, api_key, cx, start_index)
        for item in data['items']:
            if crypto_name.lower() in item['title'].lower():
                news_report += f"Title: {item['title']}\n"
                news_report += f"Summary: {item['snippet']}\n\n"
                articles_found += 1
                if articles_found == 10:
                    break
        start_index += 10

    return news_report

def get_stocktwits(crypto):
    messages = []
    print(f"Fetching StockTwits data for {crypto}...")
    with requests.Session() as session:  # using connection pooling
        r = session.get(f"https://api.stocktwits.com/api/2/streams/symbol/{crypto}.X.json")
        if r.status_code != 200:
            print(f"Error while fetching StockTwits data: {r.status_code}, {r.text}")
            return messages

        data = r.json()
        print(f"Received the following data from StockTwits: {data}")
        
        # Gather all messages
        while data.get('messages'):
            for msg in data['messages']:
                message_body = msg['body']
                # Ignore messages that mention other cryptocurrencies
                if re.search(r'\$[A-Za-z]+', message_body.replace(f'${crypto}', '')) is None:
                    messages.append(message_body)
                    # Stop fetching messages once we have 10
                    if len(messages) >= 10:
                        return messages
            last_id = data['messages'][-1]['id']
            r = session.get(f"https://api.stocktwits.com/api/2/streams/symbol/{crypto}.X.json?max={last_id}")
            if r.status_code != 200:
                print(f"Error while fetching StockTwits data: {r.status_code}, {r.text}")
                break
            data = r.json()
    return messages



def write_news_to_file(crypto_name, api_key, cx, filename):
    start_index = 1
    articles_found = 0
    with open(filename, 'a', encoding='utf-8') as f:  # specify encoding here
        f.write("News Articles:\n")
        while articles_found < 10:
            data = search_articles(crypto_name, api_key, cx, start_index)
            for item in data['items']:
                if crypto_name.lower() in item['title'].lower():
                    f.write(f"Title: {item['title']}\n")
                    f.write(f"Summary: {item['snippet']}\n\n")
                    articles_found += 1
                    if articles_found == 10:
                        break
            start_index += 10

def write_stocktwits_to_file(crypto, filename):
    print(f"Attempting to write StockTwits data for {crypto} to {filename}...")
    try:
        stocktwits_data = get_stocktwits(crypto)
        print(f"Received the following data from StockTwits: {stocktwits_data}")
        with open(filename, 'a', encoding='utf-8') as f:  # specify encoding here
            f.write("Stock Twits:\n")
            for i, msg in enumerate(stocktwits_data):
                f.write(f"Message {i+1}:\n{msg}\n\n")
        print("Successfully wrote StockTwits data to file.")
    except IndexError:
        print("StockTwits returned less than 10 messages.")
    except Exception as e:
        print(f"An error occurred while writing StockTwits data: {e}")




def write_report_to_file(report, filename):
    with open(filename, 'a') as f:
        f.write(report)


def crypto_analyzer(crypto_name, crypto_id, crypto_symbol):

    api_key = config.api_key
    cx = config.cx

    base_filename = 'crypto_report.txt'
    filename = generate_filename(crypto_id, base_filename)
    chart_filename = f"{crypto_id}_chart_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
    report = get_coin_data(crypto_id, chart_filename)
    write_report_to_file(report, filename)
    write_news_to_file(crypto_name, api_key, cx, filename)
    write_stocktwits_to_file(crypto_symbol, filename)

    # Load the report
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        report_text = f.read()

    # Use the chat model to analyze the report
    analysis = analyze_crypto_data(report_text, filename)

    return analysis, chart_filename


if __name__ == "__main__":
    crypto_name = input("Enter the name of the cryptocurrency for news articles (e.g., 'Bitcoin'): ")
    crypto_id = input("Enter the id of the cryptocurrency for CoinGecko (e.g., 'bitcoin'): ")
    crypto_symbol = input("Enter the symbol of the cryptocurrency for StockTwits (e.g., 'BTC'): ")

    analysis_text, chart_name = crypto_analyzer(crypto_name, crypto_id, crypto_symbol)

    print(analysis_text)
