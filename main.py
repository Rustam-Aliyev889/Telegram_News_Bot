from newspaper import Article
import requests
import configparser

# Configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# NEWS_API_KEY and TELEGRAM_TOKEN
NEWS_API_KEY = config['DEFAULT']['NEWS_API_KEY']
TELEGRAM_TOKEN = config['DEFAULT']['TELEGRAM_TOKEN']


def fetch_news():
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}'
    # a GET request to the News API
    response = requests.get(url)
    data = response.json()
    # The list of articles
    return data['articles']

# Function to summarize an article given its URL
def summarize_article(url):
    # Creates an Article object
    article = Article(url)
    # Downloads the article's content
    article.download()
    # To parse the article's content
    article.parse()
    # Uses natural language processing to the article
    article.nlp()
    return article.summary

if __name__ == '__main__':
    articles = fetch_news()
    for article in articles:
        print(article['title'])
        print("Summary:", summarize_article(article['url']))

