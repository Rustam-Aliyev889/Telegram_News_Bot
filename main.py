import nltk #NLTK (Natural Language Toolkit) is a Python for working with human language data.
from telegram import Bot, Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue, CallbackQueryHandler
from newspaper import Article
import requests
import configparser
import logging 
from datetime import time, timedelta, datetime
import pytz, telegram.error
import os

# Setting up logging configuration for troubleshooting
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

nltk.download('punkt')   # tokenizer for splitting text into individual sentences


NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

#config = configparser.ConfigParser()   # Configuration file
#config.read('config.ini')

#NEWS_API_KEY = config['DEFAULT']['NEWS_API_KEY']
#TELEGRAM_TOKEN = config['DEFAULT']['TELEGRAM_TOKEN']

# Gets news for NewsApi
def fetch_news():
    url = f'https://newsapi.org/v2/top-headlines?country=gb&apiKey={NEWS_API_KEY}'
    response = requests.get(url)   # a GET request to the News API
    data = response.json()
    return data['articles']   # The list of articles in JSON format


# News categories from NewsApi
def fetch_category_news(category):
    url = f'https://newsapi.org/v2/top-headlines?country=gb&category={category}&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data['articles']


# Hoposcope Api
def fetch_horoscope(sign):
    url = f"http://sandipbgt.com/theastrologer/api/horoscope/{sign.lower()}/{'today'}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return "Failed to fetch the horoscope. Please try again later."
    
    data = response.json()
    return data['horoscope']

#horoscope = fetch_horoscope("aries")
#print(horoscope)
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

def start(update: Update, context: CallbackContext) -> None:
    max_retries = 3
    current_attempt = 0
    retry_delay = 2

    while current_attempt < max_retries:
        try:
            greeting_message = (
                "Hello! 📰🔍 Looking for a quick news fix? \n\n"
                "I'm here to deliver the latest headlines with a sprinkle of summary magic, making it easy for you to stay informed."
            )
            buttons = [
                [InlineKeyboardButton("Get News 📰", callback_data='get_news')],
                [InlineKeyboardButton("Horoscope 🌟", callback_data='get_horoscope')]
            ]

            # Creates the keyboard markup
            reply_markup = InlineKeyboardMarkup(buttons)

            # Sends the greeting message and buttons
            if update.message:
                update.message.reply_text(
                    greeting_message,
                    reply_markup=reply_markup
                )
            elif update.callback_query:
                update.callback_query.message.reply_text(
                    greeting_message,
                    reply_markup=reply_markup
                )
            else:
                logger.warning("Cannot determine the type of update.")
            break  # if the message is sent successfully

        except Exception as e:
            print(f"Error occurred in /start command: {e}")
            current_attempt += 1  # Increments the attempt counter
            time(retry_delay) 

def category_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    # category buttons
    category_buttons = [
        [InlineKeyboardButton("Top News 🇬🇧 ", callback_data='category_general')],
        [InlineKeyboardButton("Science 🔬", callback_data='category_science')],
        [InlineKeyboardButton("Technology 💻", callback_data='category_technology')],
        [InlineKeyboardButton("Health 🏥", callback_data='category_health')],
        [InlineKeyboardButton("Sport 🏅", callback_data='category_sport')],
        [InlineKeyboardButton("Entertainment 🎭", callback_data='category_entertainment')],
    ]
    
    # Update the message with category buttons
    query.message.edit_text(
        text="Explore news categories: 🗞️🔎 Which category of news would you like to explore?",
        reply_markup=InlineKeyboardMarkup(category_buttons)
    )


def post_category_news(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    category = query.data.split('_')[1]
    
    articles = fetch_category_news(category)[:9]
    
    for article in articles:
        summary = summarize_article(article['url'])
        if summary is None:
            continue
        
        try:
            message_text = f"<b>{article['title']}</b>\n\n{summary} \n\n <a href='{article['url']}'>Read in full here</a>"
            context.bot.send_message(
                chat_id=query.message.chat_id,
                text=message_text,
                parse_mode=ParseMode.HTML,
                timeout=15
            )
        except telegram.error.BadRequest as e:
            # Logs the error and skips to the next article
            logging.error(f"Error sending message for article {article['title']}: {e}")
            continue
    
    # To hide the category buttons
    query.message.edit_reply_markup(reply_markup=None)
    start(update, context)

def select_sign(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    
    logger.info(f"Received sign callback: {query.data}")
    
    if query.data.startswith('sign_'):  # Checks if the callback data starts with 'sign_'
        send_horoscope(update, context, query.data.split('_')[1])  
    else:
        logger.warning("Invalid sign callback data received")

    if query.message:
        # Changes the original message to remove the sign_keyboard
        query.message.edit_text(
            text="Your cosmic secrets are about to be revealed! 🌌"
        )
    else:
        logger.warning("No message associated with the callback query.")

    query.answer()

    sign_keyboard = [
    [InlineKeyboardButton("Aries ♈", callback_data='sign_aries')],
    [InlineKeyboardButton("Taurus ♉", callback_data='sign_taurus')],
    [InlineKeyboardButton("Gemini ♊", callback_data='sign_gemini')],
    [InlineKeyboardButton("Cancer ♋", callback_data='sign_cancer')],
    [InlineKeyboardButton("Leo ♌", callback_data='sign_leo')],
    [InlineKeyboardButton("Virgo ♍", callback_data='sign_virgo')],
    [InlineKeyboardButton("Libra ♎", callback_data='sign_libra')],
    [InlineKeyboardButton("Scorpio ♏", callback_data='sign_scorpio')],
    [InlineKeyboardButton("Sagittarius ♐", callback_data='sign_sagittarius')],
    [InlineKeyboardButton("Capricorn ♑", callback_data='sign_capricorn')],
    [InlineKeyboardButton("Aquarius ♒", callback_data='sign_aquarius')],
    [InlineKeyboardButton("Pisces ♓", callback_data='sign_pisces')],
]
    # Sends message to select horoscope sign
    query.message.reply_text(
        text="Please select your horoscope sign:",
        reply_markup=InlineKeyboardMarkup(sign_keyboard)
    )


def send_horoscope(update: Update, context: CallbackContext, callback_data: str) -> None:
    zodiac_sign = callback_data.split('_')[1].lower()
    print(f"Inside send_horoscope function")
    print(f"Zodiac sign: {zodiac_sign}")

    horoscope_text = fetch_horoscope(zodiac_sign)
    sign_emojis = {
        "aries": "🐏",
        "taurus": "🐂",
        "gemini": "👯‍♂️",
        "cancer": "🦀",
        "leo": "🦁",
        "virgo": "🍂",
        "libra": "⚖️",
        "scorpio": "🦂",
        "sagittarius": "🏹",
        "capricorn": "🐐",
        "aquarius": "🌊",
        "pisces": "🐟"
    }
    if horoscope_text:
        message_text = f"Today's Horoscope for {zodiac_sign.capitalize()} {sign_emojis[zodiac_sign]} :\n\n{horoscope_text}"
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=message_text,
            parse_mode=ParseMode.HTML
        )
    else:
        update.callback_query.answer(text="Sorry, I cannot fetch the horoscope right now.")

    start(update, context)

def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    
    logger.info(f"Received callback query: {query.data}") 
    
    # Handles button clicks based on the callback data
    if query.data == 'get_news':
        logger.info("Handling get_news callback")
        category_click(update, context)
    elif query.data.startswith('category_'):
        logger.info("Handling category callback")
        post_category_news(update, context)
    elif query.data == 'get_horoscope':
        logger.info("Handling get_horoscope callback")
        select_sign(update, context)
    elif query.data.startswith('sign_'):
        logger.info("Handling sign callback")
        send_horoscope(update, context, query.data)


# Command handler for the '/news' command
def post_news(update: Update, context: CallbackContext) -> None:
    articles = fetch_news()[:10]
    
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
    start(update, context)      # Returns to the main menu after displaying news

def schedule_post_news(context: CallbackContext) -> None:
    logger.info("Executing schedule_post_news function...")
    job = context.job
    chat_id = 943389924
    articles = fetch_news()[:10]
    
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
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True, request_kwargs={'read_timeout': 20, 'connect_timeout': 20})
    dispatcher = updater.dispatcher
    job_queue: JobQueue = updater.job_queue
    chat_id = 943389924

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('news', post_news))
    dispatcher.add_handler(CallbackQueryHandler(button_click))
    dispatcher.add_handler(CallbackQueryHandler(send_horoscope))

    # Schedule for the news posting job to run at 8:00 AM and 5:00 PM UK time
    london_tz = pytz.timezone('Europe/London')
    job_queue.run_daily(schedule_post_news, time(hour=8, minute=00, tzinfo=london_tz), context=chat_id)
    job_queue.run_daily(schedule_post_news, time(hour=17, minute=00, tzinfo=london_tz), context=chat_id)
    
    updater.start_polling()
    updater.idle()