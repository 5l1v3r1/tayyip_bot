import telebot
import time
import sys
import random
import logging
from telebot import types
import requests
import json
import unicodedata
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

API_TOKEN = '<TELEGRAM_API>'

bot = telebot.TeleBot(API_TOKEN)
telebot.logger.setLevel(logging.DEBUG)

# Frequency of the random quote
LUCK_PERCENT = 2


def init():
    results = []
    repo_url = 'https://api.github.com/repos/yalanyali/tayyip_bot/contents/sounds'
    r = requests.get(repo_url)
    sounds = json.loads(r.text or r.content)
    for sound in sounds:
        name = sound["name"].split('.')[0].replace('_', ' ')
        url = sound["download_url"]
        results.append([name, url])
    return results


sounds, urls = zip(*init())


@bot.inline_handler(lambda query: len(query.query) > 2)
def query_text(inline_query):
    try:
        results = process.extract(inline_query.query, sounds, limit=10)
        result_list = []

        for result in results:
            i = results.index(result)
            r = types.InlineQueryResultAudio(
                str(i + 1), urls[sounds.index(result[0])], result[0])
            result_list.append(r)

        bot.answer_inline_query(inline_query.id, result_list)
    except Exception as e:
        print(e)


@bot.message_handler(func=lambda message: message.text.startswith('/') == False)
def echo_message(message):
    lucky_number = random.randint(1, 100)
    if lucky_number <= LUCK_PERCENT:
        text = unicodedata.normalize(
            'NFKD', message.text).encode('ascii', 'ignore')
        if lucky_number <= LUCK_PERCENT / 2:
            guess = process.extractOne(
                text, sounds, scorer=fuzz.QRatio)
        else:
            guess = process.extractOne(text, sounds)
        url = urls[sounds.index(guess[0])]
        res = requests.get(url)
        with open('temp.mp3', 'wb') as f:
            f.write(res.content)
        with open('temp.mp3', 'rb') as f:
            bot.send_voice(message.chat.id, f,
                           reply_to_message_id=message.message_id)


@bot.message_handler(commands=['luck', 'oran', 'percentage', 'kader'])
def command_image(message):
    global LUCK_PERCENT
    text = message.text
    if text[-1].isdigit():
        LUCK_PERCENT = int(filter(unicode.isdigit, text))
        bot.reply_to(message, "Oran: %" + str(LUCK_PERCENT))


def main_loop():
    bot.polling(True)
    while 1:
        time.sleep(3)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\n'
        sys.exit(0)
