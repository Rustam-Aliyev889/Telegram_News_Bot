import nltk

nltk.download('punkt')   # the 'punkt' tokenizer models from NLTK

from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
from newspaper import Article
import requests
import configparser


config = configparser.ConfigParser()   # Configuration file
config.read('config.ini')

NEWS_API_KEY = config['DEFAULT']['NEWS_API_KEY']
TELEGRAM_TOKEN = config['DEFAULT']['TELEGRAM_TOKEN']


def fetch_news():
    url = f'https://newsapi.org/v2/top-headlines?country=gb&apiKey={NEWS_API_KEY}'
    response = requests.get(url)   # a GET request to the News API
    data = response.json()
    return data['articles']   # The list of articles in JSON format


def summarize_article(url):  # Function to summarize an article given its URL
    article = Article(url) # Creates an Article object
    article.download()
    article.parse()
    if not article.text:
        return None
    article.nlp() # Uses natural language processing to the article text
    return article.summary

# Command handler for the '/start' command
def start(update: Update, context: CallbackContext) -> None:
    # A greeting message when '/start' command is received
    update.message.reply_text('Hello! I am your news bot. Type /news ')

# Command handler for the '/news' command
def post_news(update: Update, context: CallbackContext) -> None:
    articles = fetch_news()
    
    for article in articles:   # Iterates through each article and post its title, summary, and source
        summary = summarize_article(article['url'])
        if summary is None:
            continue
        # Sends a message with the article's title, summary, and source URL
        update.message.reply_text(
            f"{article['title']}\n\n{summary} \n\n Source: {article['url']}")


if __name__ == '__main__':
    updater = Updater(token=TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher            # Gets the dispatcher to register handlers
    dispatcher.add_handler(CommandHandler('start', start))       # To register the '/start' command handler
    dispatcher.add_handler(CommandHandler('news', post_news))    # To register the '/news' command handler
    updater.start_polling()      # Starts the Bot
    # Run the bot until you send a SIGINT (Ctrl+C) or the process receives a SIGTERM, SIGABRT, or SIGQUIT signal
    updater.idle()

