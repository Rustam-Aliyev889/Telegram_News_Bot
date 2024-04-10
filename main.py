import nltk
from telegram import Bot, Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue, CallbackQueryHandler
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

def fetch_category_news(category):
    url = f'https://newsapi.org/v2/top-headlines?country=gb&category={category}&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data['articles']

def fetch_horoscope(sign):
    url = f"http://sandipbgt.com/theastrologer/api/horoscope/{sign.lower()}/{'today'}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return "Failed to fetch the horoscope. Please try again later."
    
    data = response.json()
    return data['horoscope']

horoscope = fetch_horoscope("aries")
print(horoscope)
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
    greeting_message = (
        "Hello! I am your news bot. I can provide you with the latest top news articles.\n\n"
        "This bot fetches the latest top news articles from various sources and provides summaries for easy reading."
    )
    buttons = [
        [InlineKeyboardButton("Get News 📰", callback_data='get_news')],
        [InlineKeyboardButton("Horoscope 🌟", callback_data='get_horoscope')]

    ]
    
    # Creates the keyboard markup
    reply_markup = InlineKeyboardMarkup(buttons)
    
    # Sends the greeting message and buttons
    update.message.reply_text(
        greeting_message,
        reply_markup=reply_markup
    )

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
        text="Please select a category:",
        reply_markup=InlineKeyboardMarkup(category_buttons)
    )


def post_category_news(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    category = query.data.split('_')[1]  # Extract category from callback data
    
    articles = fetch_category_news(category)[:8]
    
    for article in articles:
        summary = summarize_article(article['url'])
        if summary is None:
            continue
        
        message_text = f"<b>{article['title']}</b>\n\n{summary} \n\n <a href='{article['url']}'>Read in full here</a>"
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=message_text,
            parse_mode=ParseMode.HTML
        )


def select_sign(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    
    logger.info(f"Received sign callback: {query.data}")
    
    if query.data.startswith('sign_'):  # Checks if the callback data starts with 'sign_'
        send_horoscope(update, context, query.data.split('_')[1])  
    else:
        logger.warning("Invalid sign callback data received")

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
    
    query.message.reply_text(
        text="Please select your horoscope sign:",
        reply_markup=InlineKeyboardMarkup(sign_keyboard)
    )
    
    query.answer()



def send_horoscope(update: Update, context: CallbackContext, callback_data: str) -> None:
    zodiac_sign = callback_data.split('_')[1].lower()
    print(f"Inside send_horoscope function")
    print(f"Zodiac sign: {zodiac_sign}")

    horoscope_text = fetch_horoscope(zodiac_sign)
    
    if horoscope_text:
        message_text = f"Today's Horoscope for {zodiac_sign.capitalize()}:\n\n{horoscope_text}"
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=message_text,
            parse_mode=ParseMode.HTML
        )
    else:
        update.callback_query.answer(text="Sorry, I cannot fetch the horoscope right now.")




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