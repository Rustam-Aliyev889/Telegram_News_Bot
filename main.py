import nltk

# the 'punkt' tokenizer models from NLTK
nltk.download('punkt')

from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
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
    url = f'https://newsapi.org/v2/top-headlines?country=gb&apiKey={NEWS_API_KEY}'
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

# Command handler for the '/start' command
def start(update: Update, context: CallbackContext) -> None:
    # A greeting message when '/start' command is received
    update.message.reply_text('Hello! I am your news bot. Type /news ')

# Command handler for the '/news' command
def post_news(update: Update, context: CallbackContext) -> None:
    articles = fetch_news()
    # Iterates through each article and post its title, summary, and source
    for article in articles:
        summary = summarize_article(article['url'])
        # Sends a message with the article's title, summary, and source URL
        update.message.reply_text(
            f"{article['title']}\n\n{summary} \n\n Source: {article['url']}")


if __name__ == '__main__':
    updater = Updater(token=TELEGRAM_TOKEN)
    # Gets the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # To register the '/start' command handler
    dispatcher.add_handler(CommandHandler('start', start))
    # To register the '/news' command handler
    dispatcher.add_handler(CommandHandler('news', post_news))
    # Starts the Bot
    updater.start_polling()
    # Run the bot until you send a SIGINT (Ctrl+C) or the process receives a SIGTERM, SIGABRT, or SIGQUIT signal
    updater.idle()

