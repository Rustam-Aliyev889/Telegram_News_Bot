import nltk
from telegram import Bot, Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
from newspaper import Article
import requests
import configparser
import logging 
from datetime import time, timedelta, datetime
import pytz


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

nltk.download('punkt')   # the 'punkt' tokenizer models from NLTK

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
    article = Article(url)
    try:
        article.download()
        article.parse()
    except Exception as e:
        logger.error(f"Error parsing article: {e}")
        return None
    
    # Checks for specific error messages indicating privacy policy or terms of service restrictions
    if "privacy" in article.text.lower() or "terms of service" in article.text.lower():
        logger.warning(f"Privacy policy or terms of service restriction encountered for article: {url}")
        return None
    
    if not article.text:
        logger.warning(f"No text content found for article: {url}")
        return None
    
    try:
        article.nlp()  # Uses natural language processing to the article text
    except Exception as e:
        logger.error(f"Error processing article: {e}")
        return None
    
    return article.summary

# Command handler for the '/start' command
def start(update: Update, context: CallbackContext) -> None:
    # A greeting message when '/start' command is received
    update.message.reply_text('Hello! I am your news bot. Type /news ')

# Command handler for the '/news' command
def post_news(update: Update, context: CallbackContext) -> None:
    articles = fetch_news()[:5]
    
    for article in articles:   # Iterates through each article and post its title, summary, and source
        summary = summarize_article(article['url'])
        if summary is None:
            continue
        # Sends a message with the article's title, summary, and source URL
        message_text = f"<b>{article['title']}</b>\n\n{summary} \n\n <a href='{article['url']}'>Read in full here</a>"
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message_text,
            parse_mode=ParseMode.HTML
        )


def schedule_post_news(context: CallbackContext) -> None:
    logger.info("Executing schedule_post_news function...")
    job = context.job
    chat_id = 943389924
    articles = fetch_news()[:5]
    
    for article in articles:
        summary = summarize_article(article['url'])
        if summary is None:
            continue
        
        message_text = f"<b>{article['title']}</b>\n\n{summary} \n\n <a href='{article['url']}'>Read in full here</a>"
        context.bot.send_message(
            chat_id=chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML,
            timeout=60
        )

if __name__ == '__main__':
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    job_queue: JobQueue = updater.job_queue
    chat_id = 943389924

    # Schedule for the news posting job to run at 8:00 AM and 5:00 PM UK time
    london_tz = pytz.timezone('Europe/London')
    job_queue.run_daily(schedule_post_news, time(hour=19, minute=13, tzinfo=london_tz), context=chat_id)
    job_queue.run_daily(schedule_post_news, time(hour=19, minute=19, tzinfo=london_tz), context=chat_id)
    
    updater.start_polling()
    updater.idle()