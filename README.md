# News / Horoscope Bot for Telegram
## What it does ?

Stay ahead of the game with the latest updates from various news sources, all conveniently summarized and delivered straight to you in Telegram. With features like automatic posting of top news twice a day, ability to pick a topic you are interested in and personalized daily horoscopes. Don't miss out on staying informed and entertained - get the news you need, when you need it.

## My motivation.

Ever felt bored sifting through news articles? I know the struggle! Ads popping up, lengthy reads taking forever to finish – it's exhausting. But what if you could breeze through more articles in one sitting? That's where my solution comes in. I've created a way for you to choose: browse through concise summaries, and if something catches your eye, dive deeper with just a click. No more feeling like you're drowning in unnecessary details.. It's all about getting you the news you want, how you want it.

## DEMO

<img src="https://github.com/Rustam-Aliyev889/Telegram_News_Bot/blob/main/Demo.mp4" alt="Jolt demo" height="450" align="center">

## Features

| Feature  |  Coded?       | Description  |
|----------|:-------------:|:-------------|
| `/start` | &#10004; | Kickstart the bot and be greeted with two intriguing options: News or Horoscope.|
| `/news` | &#10004; | Receive a selection of the top 10 news articles from the UK. |
| Autoposting | &#10004; | Deliver the latest headlines effortlessly with scheduled posts at 8 AM and 5 PM daily. |
| Summarised news | &#10004; | Stay informed on the go with concise summaries of the latest news updates. |
| News Categories | &#10004; | Ability to select news from a diverse range of six categories. |
|  Full article | &#10004; | Enjoy the freedom to dive deeper into any article by seamlessly accessing the full content via a provided link. |
| Horoscope | &#10004; | Start your day with personalized insights by selecting your sign to receive your daily horoscope. |
| Persistent menu | &#10004; | Use the Bot's features seamlessly with a constant menu. Once you make a choice, you'll always have the option to switch between news and horoscope effortlessly.|


## Installation

1. Create a bot with Telegram's [Bot Father](https://telegram.me/botfather) bot. A guide to creating a bot with Bot Father can be found [here](<https://core.telegram.org/bots#6-botfather>).
2. Pass in your bot's API token in `main.py`:
```python
TELEGRAM_TOKEN = 'token'  # insert your telegram bot token here
```
3. Create an account with [newsapi.org](https://newsapi.org/) to get your newsapi key.

4. Pass in your key for newsapi in `newsfeed.py`:
```python
NEWS_API_KEY = 'key'  # insert your newsapi key here
```
5. Install requirements.
6. The bot is now ready. Run `main.py` to run the bot.

