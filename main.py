import requests
import configparser

# Configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# NEWS_API_KEY and TELEGRAM_TOKEN
NEWS_API_KEY = config['DEFAULT']['NEWS_API_KEY']
TELEGRAM_TOKEN = config['DEFAULT']['TELEGRAM_TOKEN']

# Use the API keys and tokens in your code
print(NEWS_API_KEY)
print(TELEGRAM_TOKEN)


def fetch_news():
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data['articles']

if __name__ == '__main__':
    articles = fetch_news()
    for article in articles:
        print(article['title'])
